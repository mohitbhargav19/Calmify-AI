import logging
import json
from mental_health.utils import make_json_safe
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .pdf_utils import generate_dashboard_pdf

from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .question_bank import QUESTION_BANK
from .profile_questions import PROFILE_QUESTIONS
from .serializers import AssessmentSubmitSerializer
from .ml_engine import run_all_models

logger = logging.getLogger(__name__)


# ============================================================
# BASIC PAGE VIEWS
# ============================================================

from django.contrib.auth.decorators import login_required

def home_view(request):
    return render(request, "index.html")


@login_required(login_url="login")
def assessment_page(request):
    return render(request, "assessment.html")

@login_required
def download_report(request):

    dashboard_data = request.session.get("latest_dashboard_data")

    if dashboard_data is None:
        return HttpResponse("No assessment found.")

    return generate_dashboard_pdf(
        dashboard_data=dashboard_data,
        user=request.user
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def signup_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username:
            return render(
                request,
                "signup.html",
                {"error": "Username is required."}
            )

        if not email:
            return render(
                request,
                "signup.html",
                {"error": "Email is required."}
            )

        if password != confirm_password:
            return render(
                request,
                "signup.html",
                {"error": "Passwords do not match."}
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "signup.html",
                {"error": "Username already exists."}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "signup.html",
                {"error": "Email already registered."}
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("login")

    return render(request, "signup.html")


def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request=request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(
            request,
            "login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(request, "login.html")


@login_required(login_url="login")
def logout_view(request):

    logout(request)

    return redirect("home")


# ============================================================
# COMMON HELPERS
# ============================================================

def risk_class(value):
    """
    Returns CSS class based on severity label.
    """

    if value is None:
        return "neutral"

    value = str(value).strip().lower()

    high_keywords = {
        "high",
        "severe",
        "critical",
        "poor",
        "distress",
        "at risk"
    }

    moderate_keywords = {
        "moderate",
        "medium",
        "borderline"
    }

    low_keywords = {
        "low",
        "good",
        "healthy",
        "normal",
        "stable",
        "improve"
    }

    if any(word in value for word in high_keywords):
        return "high"

    if any(word in value for word in moderate_keywords):
        return "moderate"

    if any(word in value for word in low_keywords):
        return "low"

    return "neutral"


# ============================================================
# DASHBOARD
# ============================================================

@login_required(login_url="login")
def dashboard_view(request):
    """
    Displays the latest assessment dashboard stored in session.
    """

    dashboard_data = request.session.get("latest_dashboard_data")

    if not dashboard_data:
        return render(
            request,
            "dashboard.html",
            {
                "error": (
                    "No assessment data found. "
                    "Please complete the assessment first."
                )
            },
        )

    # -------------------------------------------------------
    # Safe extraction
    # -------------------------------------------------------

    dashboard = dashboard_data.get("dashboard") or {}
    predictions = dashboard_data.get("predictions") or {}
    recommendations = dashboard_data.get("recommendations") or {}
    combined_summary = dashboard_data.get("combined_summary") or {}

    user = dashboard.get("user") or {}
    summary_card = dashboard.get("summary_card") or {}
    dashboard_cards = dashboard.get("dashboard_cards") or {}
    music_support = dashboard.get("music_support") or {}
    recommendation_cards = dashboard.get("recommendation_cards") or {}

    # -------------------------------------------------------
    # Summary values
    # -------------------------------------------------------

    overall_risk_level = (
        summary_card.get("overall_risk_level")
        or combined_summary.get("overall_risk_level")
        or "Unknown"
    )

    mental_health_status = (
        summary_card.get("mental_health_status")
        or combined_summary.get("mental_health_status_label")
        or combined_summary.get("mental_health_status")
        or "Unknown"
    )

    stress_type = (
        summary_card.get("stress_type")
        or combined_summary.get("stress_type_label")
        or combined_summary.get("stress_type_prediction")
        or "Unknown"
    )

    burnout_level = (
        summary_card.get("burnout_level")
        or dashboard_cards.get("burnout_level")
        or "Unknown"
    )

    wellness_level = (
        summary_card.get("wellness_level")
        or dashboard_cards.get("wellness_level")
        or "Unknown"
    )

    # -------------------------------------------------------
    # Context
    # -------------------------------------------------------

    context = {

        # complete payloads
        "dashboard": dashboard,
        "predictions": predictions,
        "recommendations": recommendations,
        "combined_summary": combined_summary,

        # ---------------- User ----------------

        "dashboard_user": user,
        "user_name": user.get("name", request.user.username),
        "user_age": user.get("age"),
        "user_gender": user.get("gender"),
        "user_occupation": user.get("occupation"),

        # ---------------- Summary ----------------

        "overall_risk_level": overall_risk_level,
        "mental_health_status": mental_health_status,
        "stress_type": stress_type,
        "burnout_level": burnout_level,
        "wellness_level": wellness_level,

        # ---------------- Dashboard Cards ----------------

        "burnout_score": dashboard_cards.get("burnout_score"),
        "wellness_score": dashboard_cards.get("wellness_score"),
        "stress_risk_score": dashboard_cards.get("stress_risk_score"),

        "student_stress_level": dashboard_cards.get(
            "student_stress_level"
        ),

        "student_stress_level_label": dashboard_cards.get(
            "student_stress_level_label"
        ),

        "student_risk_band": dashboard_cards.get(
            "student_risk_band"
        ),

        # ---------------- Music ----------------

        "music_effect_label": music_support.get(
            "music_effect_label"
        ),

        "music_effect_prediction": music_support.get(
            "music_effect_prediction"
        ),

        "recommended_genres": music_support.get(
            "recommended_genres",
            [],
        ),

        "music_reasoning": music_support.get(
            "music_reasoning",
            [],
        ),

        # ---------------- Recommendations ----------------

        "top_recommendations": recommendation_cards.get(
            "top_recommendations",
            [],
        ),

        "alerts": recommendation_cards.get(
            "alerts",
            [],
        ),

        "self_care_plan": recommendation_cards.get(
            "self_care_plan",
            [],
        ),

        "coping_tips": recommendation_cards.get(
            "coping_tips",
            [],
        ),

        "follow_up_actions": recommendation_cards.get(
            "follow_up_actions",
            [],
        ),

        "music_recommendations": recommendation_cards.get(
            "music_recommendations",
            [],
        ),

        "positive_signals": (
            recommendation_cards.get("positive_signals")
            or recommendations.get("positive_signals", [])
        ),

        "red_flags": (
            recommendation_cards.get("red_flags")
            or recommendations.get("red_flags", [])
        ),

        # ---------------- CSS Classes ----------------

        "overall_risk_class": risk_class(overall_risk_level),
        "mental_status_class": risk_class(mental_health_status),
        "stress_type_class": risk_class(stress_type),
        "burnout_class": risk_class(burnout_level),
        "wellness_class": risk_class(wellness_level),
    }

    return render(
        request,
        "dashboard.html",
        context,
    )
    
# ============================================================
# API : ASSESSMENT QUESTIONS
# ============================================================

class AssessmentQuestionsView(APIView):
    """
    Returns all profile questions and assessment sections.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        try:

            return Response(
                {
                    "success": True,
                    "message": "Assessment questions fetched successfully.",
                    "data": {
                        "profile_questions": PROFILE_QUESTIONS,
                        "assessment_sections": QUESTION_BANK,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:

            logger.exception("Failed to load assessment questions.")

            return Response(
                {
                    "success": False,
                    "message": "Unable to fetch assessment questions.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ============================================================
# API : SUBMIT ASSESSMENT
# ============================================================

class AssessmentSubmitView(APIView):
    """
    Validates payload,
    runs complete Calmify ML pipeline,
    stores dashboard into session,
    returns prediction response.
    """

    def post(self, request):

        try:

            serializer = AssessmentSubmitSerializer(
                data=request.data
            )

            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data

            profile_answers = validated_data.get("profile") or {}
            assessment_answers = validated_data.get("answers") or {}

            logger.info(
                "Running Calmify AI prediction pipeline..."
            )

            result = run_all_models(
                profile_answers=profile_answers,
                assessment_answers=assessment_answers,
            )

            # ----------------------------------------
            # Convert everything into JSON-safe objects
            # ----------------------------------------

            result = make_json_safe(result)

            # ----------------------------------------
            # Debug JSON Serialization
            # ----------------------------------------

            try:
                json.dumps(result)
                print("JSON SAFE SUCCESS")

            except Exception as e:

                print("JSON FAILED")
                print(type(e))
                print(e)

                import pprint
                pprint.pprint(result)

                raise

            # ----------------------------------------

            if not result.get("success"):

                logger.error(
                    "Prediction pipeline failed."
                )

                return Response(
                    {
                        "success": False,
                        "message": result.get(
                            "message",
                            "Assessment processing failed."
                        ),
                        "error": result.get("error"),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # ----------------------------------------
            # Save dashboard in session
            # ----------------------------------------

            request.session["latest_dashboard_data"] = result
            request.session.modified = True

            logger.info(
                "Assessment completed successfully."
            )

            return Response(
                {
                    "success": True,
                    "message": "Assessment completed successfully.",
                    "data": result,
                    "redirect_url": "/dashboard/",
                },
                status=status.HTTP_200_OK,
            )

        except ValidationError as exc:

            logger.warning(
                "Assessment validation failed.",
                extra={
                    "errors": exc.detail
                }
            )

            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": exc.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as exc:

            print("OUTER EXCEPTION")
            print(type(exc))
            print(exc)

            logger.exception(
                "Unexpected error during assessment."
            )

            return Response(
                {
                    "success": False,
                    "message": "Failed to process assessment.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            



    