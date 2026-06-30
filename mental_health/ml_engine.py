import logging
from typing import Any, Dict

from .ai_model import predict_user_assessment
from .recommendation_engine import generate_recommendations
from mental_health.utils import make_json_safe
logger = logging.getLogger(__name__)


class MentalHealthMLEngine:
    """
    Central orchestration layer.

    Responsibilities
    ----------------
    1. Run prediction pipeline
    2. Run recommendation engine
    3. Build dashboard response
    """

    def run_full_assessment(
        self,
        profile_answers: Dict[str, Any],
        assessment_answers: Dict[str, Any],
    ) -> Dict[str, Any]:

        try:

            profile_answers = profile_answers or {}
            assessment_answers = assessment_answers or {}

            logger.info("Starting prediction pipeline.")

            # --------------------------------------------------
            # STEP 1 : Prediction Pipeline
            # --------------------------------------------------

            prediction_result = predict_user_assessment(
                profile_answers=profile_answers,
                assessment_answers=assessment_answers,
            )

            if (
                not prediction_result
                or not prediction_result.get("success", False)
            ):

                logger.error("Prediction pipeline failed.")

                return {
                    "success": False,
                    "message": prediction_result.get(
                        "message",
                        "Prediction pipeline failed.",
                    ),
                    "error": prediction_result.get("error"),
                }

            predictions = (
                prediction_result.get("predictions")
                or {}
            )

            combined_summary = (
                prediction_result.get("combined_summary")
                or {}
            )

            model_inputs = (
                prediction_result.get("model_inputs")
                or {}
            )

            failed_models = (
                prediction_result.get("failed_models")
                or {}
            )

            # --------------------------------------------------
            # DEBUG OUTPUT
            # --------------------------------------------------

            import pprint

            print("\n========== PREDICTIONS ==========")
            pprint.pprint(predictions)

            print("\n========== COMBINED SUMMARY ==========")
            pprint.pprint(combined_summary)
            # --------------------------------------------------
            # STEP 2 : Recommendation Engine
            # --------------------------------------------------

            logger.info("Generating recommendations.")

            recommendations = generate_recommendations(
                assessment_answers=assessment_answers,
                profile_answers=profile_answers,
                prediction_bundle=prediction_result,
            )

            recommendations = recommendations or {}

            # --------------------------------------------------
            # STEP 3 : Dashboard Builder
            # --------------------------------------------------

            logger.info("Building dashboard response.")

            dashboard = self._build_dashboard_response(
                profile_answers=profile_answers,
                predictions=predictions,
                combined_summary=combined_summary,
                recommendations=recommendations,
                failed_models=failed_models,
            )
            logger.info("Assessment completed successfully.")

            result = {
                "success": True,
                "profile": profile_answers,
                "model_inputs": model_inputs,
                "predictions": predictions,
                "combined_summary": combined_summary,
                "recommendations": recommendations,
                "dashboard": dashboard,
                "failed_models": failed_models,
            }

            return make_json_safe(result)

        except Exception as exc:

            logger.exception(
                "Unexpected error inside MentalHealthMLEngine."
            )

            error_result = {
                "success": False,
                "message": "ML Engine execution failed.",
                "error": str(exc),
            }

            return make_json_safe(error_result)

    def _build_dashboard_response(
        self,
        profile_answers: Dict[str, Any],
        predictions: Dict[str, Any],
        combined_summary: Dict[str, Any],
        recommendations: Dict[str, Any],
        failed_models: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Converts raw ML outputs into a frontend-friendly dashboard.
        """

        predictions = predictions or {}
        combined_summary = combined_summary or {}
        recommendations = recommendations or {}
        failed_models = failed_models or {}

        # ---------------------------------------------------
        # Individual Model Outputs
        # ---------------------------------------------------

        burnout = predictions.get("burnout") or {}

        wellness = predictions.get("wellness") or {}

        mental_health = (
            predictions.get("mental_health_status") or {}
        )

        student_survey = (
            predictions.get("student_survey") or {}
        )

        mxmh_case1 = (
            predictions.get("mxmh_case1") or {}
        )

        mxmh_case2 = (
            predictions.get("mxmh_case2") or {}
        )

        stress_dataset = (
            predictions.get("stress_dataset") or {}
        )

        # ---------------------------------------------------
        # Dashboard
        # ---------------------------------------------------

        dashboard = {

            # =================================================
            # USER
            # =================================================

            "user": {

                "name":
                    profile_answers.get("name", ""),

                "age":
                    profile_answers.get("age"),

                "gender":
                    profile_answers.get("gender"),

                "occupation":
                    profile_answers.get(
                        "occupation",
                        profile_answers.get(
                            "course",
                            "Student"
                        ),
                    ),
            },

            # =================================================
            # SUMMARY CARD
            # =================================================

            "summary_card": {

                "overall_risk_level":
                    combined_summary.get(
                        "overall_risk_level",
            "Unknown",
        ),

    "mental_health_status":
        mental_health.get(
            "prediction_label",
            "Unknown",
        ),

    "stress_type":
        stress_dataset.get(
            "prediction_label",
            "Unknown",
        ),

    "music_effect":
        mxmh_case2.get(
            "prediction_label",
            "Unknown",
        ),

    "burnout_level":
        burnout.get(
            "prediction_label",
            "Unknown",
        ),

    "wellness_level":
        wellness.get(
            "prediction_label",
            "Unknown",
        ),
},
            # =================================================
            # DASHBOARD CARDS
            # =================================================

            "dashboard_cards": {

    "burnout_prediction":
        burnout.get(
            "prediction_label"
        ),

    "burnout_confidence":
        burnout.get(
            "confidence"
        ),

    "wellness_prediction":
        wellness.get(
            "prediction_label"
        ),

    "wellness_confidence":
        wellness.get(
            "confidence"
        ),

    "mental_health_prediction":
        mental_health.get(
            "prediction_label"
        ),

    "mental_health_confidence":
        mental_health.get(
            "confidence"
        ),

    "student_stress_prediction":
        student_survey.get(
            "prediction_label"
        ),

    "student_stress_confidence":
        student_survey.get(
            "confidence"
        ),

    "stress_dataset_prediction":
        stress_dataset.get(
            "prediction_label"
        ),

    "stress_dataset_confidence":
        stress_dataset.get(
            "confidence"
        ),

},

            # =================================================
            # MUSIC SUPPORT
            # =================================================

            "music_support": {

    "music_effect_prediction":
        mxmh_case2.get(
            "prediction"
        ),

    "music_effect_label":
        mxmh_case2.get(
            "prediction_label"
        ),

    "recommended_genres":
        mxmh_case1.get(
            "recommended_genres",
            [],
        ),

    "music_reasoning":
        mxmh_case1.get(
            "reasoning",
            [],
        ),
},

            # =================================================
            # RECOMMENDATIONS
            # =================================================

            "recommendation_cards": {

                "top_recommendations":
                    recommendations.get(
                        "top_recommendations",
                        [],
                    ),

                "alerts":
                    recommendations.get(
                        "alerts",
                        [],
                    ),

                "self_care_plan":
                    recommendations.get(
                        "self_care_plan",
                        [],
                    ),

                "coping_tips":
                    recommendations.get(
                        "coping_tips",
                        [],
                    ),

                "follow_up_actions":
                    recommendations.get(
                        "follow_up_actions",
                        [],
                    ),

                "music_recommendations":
                    recommendations.get(
                        "music_recommendations",
                        [],
                    ),

                "red_flags":
                    recommendations.get(
                        "red_flags",
                        [],
                    ),

                "positive_signals":
                    recommendations.get(
                        "positive_signals",
                        [],
                    ),
            },

            # =================================================
            # MODEL STATUS
            # =================================================

            "model_status": {

                "failed_models":
                    failed_models,

                "working_models":

                    [

                        name

                        for name in predictions.keys()

                        if name not in failed_models

                    ],
            },
        }

        return dashboard
    
    
# ============================================================
# Singleton Instance
# ============================================================

ml_engine = MentalHealthMLEngine()


# ============================================================
# Public Wrapper
# ============================================================

def run_all_models(
    profile_answers: Dict[str, Any],
    assessment_answers: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Public API used by views.py.

    Runs the complete ML pipeline:
        1. Prediction
        2. Recommendation
        3. Dashboard Builder
    """

    return ml_engine.run_full_assessment(
        profile_answers=profile_answers,
        assessment_answers=assessment_answers,
    )