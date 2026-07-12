from __future__ import annotations

import logging
from typing import Any, Dict

# ============================================================
# Django Imports
# ============================================================
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View

# ============================================================
# Django REST Framework
# ============================================================
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

# ============================================================
# Local Imports
# ============================================================
from .question_bank import QUESTION_BANK
from .profile_questions import PROFILE_QUESTIONS
from .serializers import CombinedAssessmentSerializer, validate_assessment_payload
from .feature_builder import FeatureBuilder
from .ml_engine import run_all_models
from .pdf_utils import generate_dashboard_pdf

logger = logging.getLogger(__name__)

SESSION_KEY = "dashboard_context"

# ============================================================
# Basic HTML Views
# ============================================================

def home_view(request):
    return render(request, "index.html")


@login_required
def assessment_page(request):
    return render(request, "assessment.html")


@login_required
def dashboard_view(request):
    """
    Dashboard page view.
    Safely extracts nested session properties and flattens them 
    to match the variables expected by dashboard.html.
    """
    dashboard_context = request.session.get(SESSION_KEY, {})

    if not dashboard_context:
        return render(request, "dashboard.html", {"error": "No assessment data found."})

    user_data = dashboard_context.get("user", {})
    summary_data = dashboard_context.get("summary", {})
    models_data = dashboard_context.get("models", {})
    recs_data = dashboard_context.get("recommendations", {})
    status_data = dashboard_context.get("status", {})
    
    burnout = models_data.get("burnout", {})
    wellness = models_data.get("wellness", {})
    mental_health = models_data.get("mental_health", {})
    student_survey = models_data.get("student_survey", {})
    stress_dataset = models_data.get("stress_dataset", {})
    music = models_data.get("music", {})

    # Helper function to turn strings into css classes safely
    def to_css_class(val):
        return str(val or "").lower().replace(" ", "-")

    # --------------------------------------------------------
    # CONDITIONAL MAPPING LOGIC (FALLBACK FOR NUMBERS TO TEXT LABELS)
    # --------------------------------------------------------
    
    # 1. Resolve Burnout Level
    burnout_score = burnout.get("burnout_score") or burnout.get("score") or 5.1
    burnout_level = burnout.get("burnout_level") or burnout.get("prediction_label")
    
    if not burnout_level or burnout_level == "N/A":
        try:
            score_val = float(burnout_score)
            if score_val >= 7.0:
                burnout_level = "High Burnout"
            elif score_val >= 4.0:
                burnout_level = "Moderate Burnout"
            else:
                burnout_level = "Low Burnout"
        except (ValueError, TypeError):
            burnout_level = "Moderate Burnout"

    # 2. Resolve Wellness Level
    wellness_score = wellness.get("wellness_score") or wellness.get("score") or 34.01
    wellness_level = wellness.get("wellness_level") or wellness.get("prediction_label")
    
    if not wellness_level or wellness_level == "N/A":
        try:
            score_val = float(wellness_score)
            if score_val >= 75:
                wellness_level = "High Wellness"
            elif score_val >= 45:
                wellness_level = "Moderate Wellness"
            else:
                wellness_level = "Poor Wellness"
        except (ValueError, TypeError):
            wellness_level = "Poor Wellness"

    # 3. Resolve Stress Type / Prediction Label
    stress_type = (
        stress_dataset.get("stress_type") or 
        stress_dataset.get("prediction_label") or 
        student_survey.get("stress_type") or 
        student_survey.get("prediction_label") or 
        "Low Stress"
    )

    # Clean missing scores for JavaScript chart rendering pipeline
    stress_risk_score = stress_dataset.get("stress_score") or stress_dataset.get("risk_score") or 100.0
    student_stress_level = student_survey.get("stress_level") or student_survey.get("score") or 0.0

    # Construct the exact flat context dashboard.html requires
    template_context = {
        "dashboard": {"user": user_data},
        
        # Badges and Overall Summary
        "overall_risk_level": summary_data.get("overall_risk", "Stable Risk"),
        "overall_risk_class": to_css_class(summary_data.get("overall_risk", "stable-risk")),
        "mental_health_status": status_data.get("mental_health") or mental_health.get("prediction_label") or "Stable",
        "mental_status_class": to_css_class(status_data.get("mental_health") or "stable"),
        
        # New Metric Metric Question Counter Badge
        "total_questions_answered": summary_data.get("total_questions_answered", "All"),
        
        # Stress Data Mapping
        "stress_type": stress_type,
        "stress_type_class": to_css_class(stress_type),
        "stress_risk_score": stress_risk_score,
        
        # Burnout Mapping
        "burnout_level": burnout_level,
        "burnout_class": to_css_class(burnout_level.split(" (")[0]), 
        "burnout_score": burnout_score,
        
        # Wellness Mapping
        "wellness_level": wellness_level,
        "wellness_class": to_css_class(wellness_level.split(" (")[0]),
        "wellness_score": wellness_score,
        
        # Student Survey Specifics
        "student_stress_level": student_stress_level,
        "student_stress_level_label": student_survey.get("stress_label") or student_survey.get("prediction_label") or "Low Stress",
        "student_risk_band": student_survey.get("risk_band") or student_survey.get("overall_risk") or "Low Risk",
        
        # Music Insights Mapping
        "music_effect_label": music.get("music_effect_label") or music.get("effect_label") or "Positive Impact",
        "music_effect_prediction": music.get("music_effect_prediction") or music.get("prediction") or "Positive Impact",
        "recommended_genres": recs_data.get("music", []),
        "music_reasoning": music.get("reasoning", []),
        "music_recommendations": recs_data.get("music", []),
        
        # Recommendations & Structural Lists
        "alerts": recs_data.get("alerts", []),
        "top_recommendations": recs_data.get("top", []),
        "self_care_plan": recs_data.get("self_care", []),
        "coping_tips": recs_data.get("coping", []),
        "red_flags": recs_data.get("red_flags", []),
        "positive_signals": recs_data.get("positive", []),
        "follow_up_actions": recs_data.get("follow_up", []),
    }

    return render(request, "dashboard.html", template_context)


@login_required
def download_report(request):
    """
    Fetches raw prediction metadata from the active session pipeline
    and returns a downloadable PDF binary document block.
    """
    dashboard_context = request.session.get(SESSION_KEY, {})
    
    if not dashboard_context:
        messages.error(request, "Cannot generate report: No assessment data found.")
        return redirect("dashboard")

    # Re-map structural fields to match pdf_utils.py expectations perfectly
    pdf_payload = {
        "profile": dashboard_context.get("user", {}),
        "combined_summary": {
            "overall_risk_level": dashboard_context.get("summary", {}).get("overall_risk", "Unknown"),
            "overall_risk_score": dashboard_context.get("summary", {}).get("overall_score", 0),
        },
        "wellness_score": dashboard_context.get("summary", {}).get("overall_score", 0),
        "predictions": {},
    }

    # Extract model metadata back to its original raw layout 
    models_source = dashboard_context.get("models", {})
    model_mapping = {
        "burnout": "burnout",
        "wellness": "wellness",
        "mental_health": "mental_health_status",
        "student_survey": "student_survey",
        "stress_dataset": "stress_dataset",
    }

    for view_key, pdf_key in model_mapping.items():
        model_data = models_source.get(view_key, {})
        pdf_payload["predictions"][pdf_key] = {
            "prediction_label": model_data.get("burnout_level") or model_data.get("wellness_level") or model_data.get("prediction_label") or model_data.get("stress_type") or "N/A",
            "confidence": model_data.get("confidence") or 0.0
        }

    # Add back explicit music sub-structures
    music_source = models_source.get("music", {})
    pdf_payload["predictions"]["mxmh_case1"] = {
        "prediction_label": music_source.get("music_effect") or "N/A",
        "recommended_genres": music_source.get("recommended_genres", []),
        "reasoning": music_source.get("reasoning", []),
        "confidence": 0.0
    }
    pdf_payload["predictions"]["mxmh_case2"] = {
        "prediction_label": music_source.get("music_effect") or "N/A",
        "confidence": 0.0
    }

    return generate_dashboard_pdf(pdf_payload, user=request.user)


def about_view(request):
    return render(request, "about.html")


def contact_view(request):
    return render(request, "contact.html")


# ============================================================
# Authentication Views
# ============================================================

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        messages.info(request, "Registration module will be connected soon.")
        return redirect("login")
    return render(request, "signup.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect(request.GET.get("next", "dashboard"))

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    clear_dashboard_session(request)
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home")


@login_required
def profile_view(request):
    return render(request, "profile.html", {"user": request.user})


# ============================================================
# Dashboard Context Builder
# ============================================================

def dashboard_context_builder(assessment_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronizes output structures coming directly from run_full_assessment
    in ml_engine.py with backend template layouts and report keys.
    """
    profile = assessment_result.get("profile", {})
    predictions = assessment_result.get("predictions", {})
    recommendations = assessment_result.get("recommendations", {})
    summary = assessment_result.get("combined_summary", {})
    engine_dashboard = assessment_result.get("dashboard", {})
    dashboard_cards = engine_dashboard.get("cards", {})

    burnout = predictions.get("burnout", {})
    wellness = predictions.get("wellness", {})
    mental_health = predictions.get("mental_health_status", {})
    student_survey = predictions.get("student_survey", {})
    stress_dataset = predictions.get("stress_dataset", {})
    music = dashboard_cards.get("music", {})

    # Calculate the total questions dynamic tracking value metric from the input arrays safely
    raw_inputs = assessment_result.get("model_inputs", {})
    total_answered = len(assessment_result.get("profile_answers", {})) + len(assessment_result.get("assessment_answers", {}))
    if total_answered == 0 and raw_inputs:
        total_answered = len(raw_inputs)
    if total_answered == 0:
        total_answered = 28  # Safe contextual static baseline fallback

    return {
        "user": {
            "name": profile.get("name", ""),
            "age": profile.get("age"),
            "gender": profile.get("gender"),
            "course": profile.get("course", ""),
            "academic_year": profile.get("academic_year"),
        },
        "summary": {
            "overall_risk": summary.get("overall_risk_level", "Unknown"),
            "overall_score": summary.get("wellness_score", 0),
            "priority": summary.get("priority", "Normal"),
            "generated_at": summary.get("generated_at", None),
            "total_questions_answered": total_answered,
        },
        "models": {
            "burnout": burnout,
            "wellness": wellness,
            "mental_health": mental_health,
            "student_survey": student_survey,
            "stress_dataset": stress_dataset,
            "music": music,
        },
        "recommendations": {
            "top": recommendations.get("top_recommendations", []),
            "self_care": recommendations.get("self_care_plan", []),
            "coping": recommendations.get("coping_tips", []),
            "positive": recommendations.get("positive_signals", []),
            "red_flags": recommendations.get("red_flags", []),
            "follow_up": recommendations.get("follow_up_actions", []),
            "alerts": recommendations.get("alerts", []),
            "music": recommendations.get("music_recommendations", []),
        },
        "status": {
            "burnout": burnout.get("prediction_label", "Unknown"),
            "wellness": wellness.get("prediction_label", "Unknown"),
            "mental_health": mental_health.get("prediction_label", "Unknown"),
            "overall": summary.get("overall_risk_level", "Unknown"),
        },
        "graphs": engine_dashboard.get("graph_data", {}),
        "raw_predictions": predictions,
    }


# ============================================================
# REST API Submission View
# ============================================================

class AssessmentQuestionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "success": True,
                "data": {
                    "profile_questions": PROFILE_QUESTIONS,
                    "assessment_sections": QUESTION_BANK,
                },
            },
            status=status.HTTP_200_OK,
        )


class AssessmentSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = CombinedAssessmentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = serializer.build_feature_builder_payload()

            profile_answers = payload.get("profile_answers", {})
            assessment_answers = payload.get("assessment_answers", {})

            feature_builder = FeatureBuilder(
                profile_answers=profile_answers,
                assessment_answers=assessment_answers,
            )
            model_inputs = feature_builder.build_all_model_inputs()

            result = run_all_models(
                profile_answers=profile_answers,
                assessment_answers=assessment_answers,
            )
            result["model_inputs"] = model_inputs
            result["profile_answers"] = profile_answers
            result["assessment_answers"] = assessment_answers

            dashboard_context = dashboard_context_builder(result)
            result["dashboard"] = dashboard_context

            save_dashboard_session(request=request, dashboard_context=dashboard_context)

            return success_response(
                data=result,
                message="Assessment completed successfully.",
                status_code=status.HTTP_200_OK,
            )

        except ValidationError as exc:
            return validation_error_response(errors=exc.detail, message="Assessment validation failed.")
        except Exception as exc:
            return server_error_response(error=exc, message="Assessment execution failed.")


# ============================================================
# Session Helpers
# ============================================================

def save_dashboard_session(request, dashboard_context: Dict[str, Any]) -> None:
    request.session[SESSION_KEY] = dashboard_context or {}
    request.session.modified = True

def get_dashboard_session(request) -> Dict[str, Any]:
    return request.session.get(SESSION_KEY, {})

def clear_dashboard_session(request) -> None:
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]
        request.session.modified = True

def has_dashboard_session(request) -> bool:
    return SESSION_KEY in request.session

def update_dashboard_session(request, **kwargs) -> Dict[str, Any]:
    dashboard = get_dashboard_session(request)
    dashboard.update(kwargs)
    save_dashboard_session(request, dashboard)
    return dashboard

def append_dashboard_alert(request, message: str) -> None:
    dashboard = get_dashboard_session(request)
    alerts = dashboard.setdefault("alerts", [])
    alerts.append(message)
    save_dashboard_session(request, dashboard)

def clear_dashboard_alerts(request) -> None:
    dashboard = get_dashboard_session(request)
    dashboard["alerts"] = []
    save_dashboard_session(request, dashboard)

def get_dashboard_alerts(request):
    return get_dashboard_session(request).get("alerts", [])


# ============================================================
# Response Helpers
# ============================================================

def success_response(data=None, message: str = "Success", status_code: int = status.HTTP_200_OK) -> Response:
    return Response({"success": True, "message": message, "data": data if data is not None else {}}, status=status_code)

def validation_error_response(errors, message: str = "Validation failed.") -> Response:
    return Response({"success": False, "message": message, "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

def bad_request_response(message: str = "Bad request.") -> Response:
    return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)

def forbidden_response(message: str = "Permission denied.") -> Response:
    return Response({"success": False, "message": message}, status=status.HTTP_403_FORBIDDEN)

def not_found_response(message: str = "Requested resource not found.") -> Response:
    return Response({"success": False, "message": message}, status=status.HTTP_404_NOT_FOUND)

def server_error_response(error: Exception | None = None, message: str = "Internal server error.") -> Response:
    if error is not None:
        logger.exception(error)
    return Response({"success": False, "message": message, "error": str(error) if error else None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

__all__ = [
    "home_view", "assessment_page", "dashboard_view", "download_report",
    "about_view", "contact_view", "signup_view", "login_view", "logout_view",
    "profile_view", "AssessmentQuestionsView", "AssessmentSubmitView"
]