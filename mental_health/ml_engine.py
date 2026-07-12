from __future__ import annotations

import logging

from typing import Any, Dict

from .ai_model import predict_user_assessment
from .recommendation_engine import generate_recommendations
from .utils import make_json_safe


logger = logging.getLogger(__name__)

# ============================================================
# PART 2
# ML Engine
# ============================================================

class MentalHealthMLEngine:
    """
    Central orchestration layer responsible for executing
    the complete Calmify AI assessment pipeline.
    """

    def __init__(self) -> None:
        """
        Reserved for future initialization.

        Future additions:
            - cache
            - telemetry
            - analytics
            - audit logging
        """

        logger.info(
            "MentalHealthMLEngine initialized."
        )
        
    def run_full_assessment(
        self,
        profile_answers: Dict[str, Any],
        assessment_answers: Dict[str, Any],
    ) -> Dict[str, Any]:

        try:

            profile_answers = profile_answers or {}
            assessment_answers = assessment_answers or {}

            logger.info("Starting assessment pipeline.")

            prediction_result = predict_user_assessment(
                profile_answers=profile_answers,
                assessment_answers=assessment_answers,
            )

            if not prediction_result.get("success", False):

                return make_json_safe({

                    "success": False,

                    "message": prediction_result.get(
                        "message",
                        "Prediction pipeline failed.",
                    ),

                    "error": prediction_result.get("error"),

                })

            predictions = prediction_result.get(
                "predictions",
                {},
            )

            combined_summary = prediction_result.get(
                "combined_summary",
                {},
            )

            model_inputs = prediction_result.get(
                "model_inputs",
                {},
            )

            failed_models = prediction_result.get(
                "failed_models",
                {},
            )

            recommendations = generate_recommendations(

                profile_answers=profile_answers,

                assessment_answers=assessment_answers,

                prediction_bundle=prediction_result,

            ) or {}

            dashboard = self._build_dashboard(

                profile_answers=profile_answers,

                predictions=predictions,

                combined_summary=combined_summary,

                recommendations=recommendations,

                failed_models=failed_models,

            )

            return make_json_safe({

                "success": True,

                "profile": profile_answers,

                "model_inputs": model_inputs,

                "predictions": predictions,

                "combined_summary": combined_summary,

                "recommendations": recommendations,

                "dashboard": dashboard,

                "failed_models": failed_models,

            })

        except Exception as exc:

            logger.exception(
                "Assessment pipeline failed."
            )

            return make_json_safe({

                "success": False,

                "message": "Assessment execution failed.",

                "error": str(exc),

            })
            
    def _build_dashboard(
        self,
        profile_answers: Dict[str, Any],
        predictions: Dict[str, Any],
        combined_summary: Dict[str, Any],
        recommendations: Dict[str, Any],
        failed_models: Dict[str, Any],
    ) -> Dict[str, Any]:

        burnout = predictions.get("burnout", {})
        wellness = predictions.get("wellness", {})
        mental = predictions.get("mental_health_status", {})
        student = predictions.get("student_survey", {})
        stress = predictions.get("stress_dataset", {})
        mxmh1 = predictions.get("mxmh_case1", {})
        mxmh2 = predictions.get("mxmh_case2", {})

        dashboard = {

            "user": {

                "name": profile_answers.get("name", ""),

                "age": profile_answers.get("age"),

                "gender": profile_answers.get("gender"),

                "occupation": profile_answers.get(
                    "occupation",
                    profile_answers.get(
                        "course",
                        "Student",
                    ),
                ),
            },

            "summary": combined_summary,

            "cards": {

                "burnout": burnout,

                "wellness": wellness,

                "mental_health": mental,

                "student_survey": student,

                "stress_dataset": stress,

                "music": {

                    "music_effect":
                        mxmh2.get(
                            "prediction_label",
                        ),

                    "recommended_genres":
                        mxmh1.get(
                            "recommended_genres",
                            [],
                        ),

                    "reasoning":
                        mxmh1.get(
                            "reasoning",
                            [],
                        ),
                },
            },

            "recommendations": recommendations,

            "graph_data": self._build_graph_data(
                predictions=predictions,
                combined_summary=combined_summary,
            ),

            "model_status": {

                "failed_models": failed_models,

                "working_models": [

                    model

                    for model in predictions.keys()

                    if model not in failed_models

                ],
            },
        }

        return make_json_safe(dashboard)
    
    def _build_graph_data(
        self,
        predictions: Dict[str, Any],
        combined_summary: Dict[str, Any],
    ) -> Dict[str, Any]:

        burnout = predictions.get("burnout", {})
        wellness = predictions.get("wellness", {})
        mental = predictions.get("mental_health_status", {})
        student = predictions.get("student_survey", {})
        stress = predictions.get("stress_dataset", {})

        return {

            "burnout_score":
                burnout.get(
                    "burnout_score",
                    burnout.get("prediction", 0),
                ),

            "wellness_score":
                wellness.get(
                    "wellness_score",
                    wellness.get("prediction", 0),
                ),

            "mental_health_prediction":
                mental.get(
                    "prediction",
                    0,
                ),

            "student_survey_prediction":
                student.get(
                    "prediction",
                    0,
                ),

            "stress_dataset_prediction":
                stress.get(
                    "prediction",
                    0,
                ),

            "overall_risk_level":
                combined_summary.get(
                    "overall_risk_level",
                    "Unknown",
                ),

            "overall_risk_score":
                combined_summary.get(
                    "overall_risk_score",
                    0,
                ),
        }
        
    # ============================================================
# SINGLETON
# ============================================================

ml_engine = MentalHealthMLEngine()

# ============================================================
# PUBLIC API
# ============================================================

def run_all_models(
    profile_answers: Dict[str, Any],
    assessment_answers: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Public entry point used by views.py.
    """

    return ml_engine.run_full_assessment(
        profile_answers=profile_answers,
        assessment_answers=assessment_answers,
    )