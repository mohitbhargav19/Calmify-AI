# ==========================================================
# ai_model.py
#
# Central AI Prediction Service
# Calmify AI
# ==========================================================

# ==========================================================
# IMPORTS
# ==========================================================

import json
import logging

from pathlib import Path

from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd

from mental_health.utils import make_json_safe

from .feature_builder import build_all_model_inputs

from .model_feature_mapper import (
    TRAINED_MODEL_KEYS,
    MODEL_FILE_MAP,
    FEATURE_COLUMNS_FILE_MAP,
    LABEL_ENCODER_FILE_MAP,
    MODEL_OUTPUT_KEY_MAP,
    BURNOUT_MODEL,
    WELLNESS_MODEL,
    MENTAL_HEALTH_STATUS_MODEL,
    STUDENT_SURVEY_MODEL,
    STRESS_DATASET_MODEL,
    MXMH_CASE2_MODEL,
)

# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(__name__)

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"

# ==========================================================
# MANUAL LABEL MAPS
# ==========================================================

MENTAL_HEALTH_LABEL_MAP = {

    0: "Healthy",

    1: "Mild Concern",

    2: "Moderate Concern",

    3: "High Risk",

    4: "Severe Risk",

    5: "Critical",

}

STUDENT_SURVEY_LABEL_MAP = {

    0: "Low Stress",

    1: "Moderate Stress",

    2: "High Stress",

}

STRESS_DATASET_LABEL_MAP = {

    0: "Low Stress",

    1: "Moderate Stress",

    2: "High Stress",

}

# ==========================================================
# AI MODEL SERVICE
# ==========================================================

class AIModelService:
    """
    Central AI Prediction Service.

    Responsibilities
    ----------------
    • Load trained models
    • Load feature columns
    • Load label encoders
    """

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(self):

        self.models: Dict[str, Any] = {}

        self.feature_columns: Dict[str, list] = {}

        self.label_encoders: Dict[str, Any] = {}

        logger.info("Initializing AIModelService...")

        self.load_models()

    # ======================================================
    # LOAD FEATURE COLUMNS
    # ======================================================

    def _load_feature_columns(
        self,
        model_key: str,
    ) -> Optional[list]:

        filename = FEATURE_COLUMNS_FILE_MAP.get(model_key)

        if filename is None:
            return None

        path = MODEL_DIR / filename

        if not path.exists():

            logger.warning(
                "Feature file not found: %s",
                path,
            )

            return None

        try:

            if path.suffix.lower() == ".json":

                with open(
                    path,
                    "r",
                    encoding="utf-8",
                ) as file:

                    columns = json.load(file)

            else:

                columns = joblib.load(path)

            if isinstance(columns, pd.Index):
                columns = columns.tolist()

            elif not isinstance(columns, list):
                columns = list(columns)

            logger.info(
                "%s feature columns loaded.",
                model_key,
            )

            return columns

        except Exception:

            logger.exception(
                "Unable to load feature columns for %s",
                model_key,
            )

            return None

    # ======================================================
    # LOAD LABEL ENCODER
    # ======================================================

    def _load_label_encoder(
        self,
        model_key: str,
    ):

        filename = LABEL_ENCODER_FILE_MAP.get(model_key)

        if filename is None:
            return None

        path = MODEL_DIR / filename

        if not path.exists():

            logger.info(
                "%s does not use LabelEncoder.",
                model_key,
            )

            return None

        try:

            encoder = joblib.load(path)

            logger.info(
                "%s label encoder loaded.",
                model_key,
            )

            return encoder

        except Exception:

            logger.exception(
                "Unable to load label encoder for %s",
                model_key,
            )

            return None

    # ======================================================
    # LOAD ALL MODELS
    # ======================================================

    def load_models(self):

        logger.info("Loading Calmify AI models...")

        self.models.clear()
        self.feature_columns.clear()
        self.label_encoders.clear()

        for model_key in TRAINED_MODEL_KEYS:

            filename = MODEL_FILE_MAP.get(model_key)

            if filename is None:
                continue

            model_path = MODEL_DIR / filename

            if not model_path.exists():

                logger.warning(
                    "%s model file missing.",
                    model_key,
                )

                continue

            try:

                self.models[model_key] = joblib.load(model_path)

                self.feature_columns[model_key] = (
                    self._load_feature_columns(model_key)
                )

                self.label_encoders[model_key] = (
                    self._load_label_encoder(model_key)
                )

                logger.info(
                    "%s loaded successfully.",
                    model_key,
                )

            except Exception:

                logger.exception(
                    "Failed loading %s",
                    model_key,
                )

    # ======================================================
    # RELOAD MODELS
    # ======================================================

    def reload_models(self):

        logger.info("Reloading AI models...")

        self.load_models()

    # ======================================================
    # MODEL STATUS
    # ======================================================

    def get_model_status(
        self,
    ) -> Dict[str, Any]:

        status = {}

        for model_key in TRAINED_MODEL_KEYS:

            status[model_key] = {

                "loaded":
                    model_key in self.models,

                "feature_columns":
                    self.feature_columns.get(model_key)
                    is not None,

                "label_encoder":
                    self.label_encoders.get(model_key)
                    is not None,

            }

        return status
    
        # ======================================================
    # ALIGN FEATURES
    # ======================================================

    def _align_features(
        self,
        model_key: str,
        features: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Align incoming feature dictionary with the
        exact feature order used during training.
        """

        columns = self.feature_columns.get(model_key)

        if columns is None:
            return pd.DataFrame([features])

        aligned = {}

        for column in columns:
            aligned[column] = features.get(column, 0)

        return pd.DataFrame([aligned])

    # ======================================================
    # DECODE CLASSIFICATION LABEL
    # ======================================================

    def _decode_prediction(
        self,
        model_key: str,
        prediction: Any,
    ) -> str:
        """
        Decode classifier outputs.
        """

        # ---------------------------------------------
        # Manual label maps
        # ---------------------------------------------

        if model_key == MENTAL_HEALTH_STATUS_MODEL:

            return MENTAL_HEALTH_LABEL_MAP.get(
                int(prediction),
                str(prediction),
            )

        if model_key == STUDENT_SURVEY_MODEL:

            return STUDENT_SURVEY_LABEL_MAP.get(
                int(prediction),
                str(prediction),
            )

        if model_key == STRESS_DATASET_MODEL:

            return STRESS_DATASET_LABEL_MAP.get(
                int(prediction),
                str(prediction),
            )

        # ---------------------------------------------
        # Label Encoder
        # ---------------------------------------------

        encoder = self.label_encoders.get(model_key)

        if encoder is None:
            return str(prediction)

        try:

            return str(

                encoder.inverse_transform(
                    np.array([prediction])
                )[0]

            )

        except Exception:

            logger.exception(
                "Label decoding failed for %s",
                model_key,
            )

            return str(prediction)

    # ======================================================
    # SINGLE MODEL PREDICTION
    # ======================================================

    def _predict_single_model(
        self,
        model_key: str,
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run prediction for one trained model.
        """

        if model_key not in self.models:

            raise RuntimeError(
                f"{model_key} model is not loaded."
            )

        model = self.models[model_key]

        X = self._align_features(
            model_key,
            features,
        )

        prediction = model.predict(X)[0]

        # ==================================================
        # BURNOUT (REGRESSION)
        # ==================================================

        if model_key == BURNOUT_MODEL:

            score = round(float(prediction), 2)

            if score < 3.33:
                level = "Low Burnout"

            elif score < 6.66:
                level = "Moderate Burnout"

            else:
                level = "High Burnout"

            return make_json_safe({

                "burnout_score": score,

                "prediction": score,

                "prediction_label": level,

                "confidence": None,

                "probabilities": {},

                "features_used": features,

            })

        # ==================================================
        # WELLNESS (REGRESSION)
        # ==================================================

        if model_key == WELLNESS_MODEL:

            score = round(float(prediction), 2)

            if score < 40:
                level = "Poor Wellness"

            elif score < 70:
                level = "Average Wellness"

            else:
                level = "Good Wellness"

            return make_json_safe({

                "wellness_score": score,

                "prediction": score,

                "prediction_label": level,

                "confidence": None,

                "probabilities": {},

                "features_used": features,

            })

        # ==================================================
        # CLASSIFICATION MODELS
        # ==================================================

        prediction = int(prediction)

        label = self._decode_prediction(
            model_key,
            prediction,
        )

        result = {

            "prediction": prediction,

            "prediction_label": label,

            "confidence": None,

            "probabilities": {},

            "features_used": features,

        }

        # ---------------------------------------------
        # Predict probabilities
        # ---------------------------------------------

        if hasattr(model, "predict_proba"):

            try:

                probabilities = model.predict_proba(X)[0]

                result["confidence"] = round(

                    float(np.max(probabilities)) * 100,

                    2,

                )

                result["probabilities"] = {

                    str(index): round(
                        float(value),
                        4,
                    )

                    for index, value in enumerate(
                        probabilities
                    )

                }

            except Exception:

                logger.exception(

                    "Probability calculation failed for %s",

                    model_key,

                )

        return make_json_safe(result)
    
        # ======================================================
    # PREDICT ALL MODELS
    # ======================================================

    def predict_all(
        self,
        model_inputs: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run inference on every trained model.
        """

        logger.info("Starting prediction pipeline...")

        predictions = {}

        failed_models = {}

        for model_key in TRAINED_MODEL_KEYS:

            try:

                features = model_inputs.get(model_key)

                if features is None:
                    continue

                output_key = MODEL_OUTPUT_KEY_MAP.get(
                    model_key,
                    model_key,
                )

                predictions[output_key] = (
                    self._predict_single_model(
                        model_key,
                        features,
                    )
                )

            except Exception as exc:

                logger.exception(
                    "Prediction failed for %s",
                    model_key,
                )

                failed_models[model_key] = str(exc)

        combined_summary = self._build_combined_summary(
            predictions,
        )

        return {

            "success": len(predictions) > 0,

            "predictions": predictions,

            "combined_summary": combined_summary,

            "failed_models": failed_models,

        }

    # ======================================================
    # BUILD COMBINED SUMMARY
    # ======================================================

    def _build_combined_summary(
        self,
        predictions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create one unified summary from all model outputs.
        """

        burnout = predictions.get("burnout", {})

        wellness = predictions.get("wellness", {})

        mental = predictions.get(
            "mental_health_status",
            {},
        )

        student = predictions.get(
            "student_survey",
            {},
        )

        stress = predictions.get(
            "stress_dataset",
            {},
        )

        mxmh = predictions.get(
            "mxmh_case2",
            {},
        )

        overall_risk = self._compute_overall_risk(
            predictions,
        )

        return {

            "overall_risk_level": overall_risk,

            "burnout_score":
                burnout.get("burnout_score"),

            "burnout_level":
                burnout.get("prediction_label"),

            "wellness_score":
                wellness.get("wellness_score"),

            "wellness_level":
                wellness.get("prediction_label"),

            "mental_health_status":
                mental.get("prediction_label"),

            "student_stress_level":
                student.get("prediction_label"),

            "stress_dataset_level":
                stress.get("prediction_label"),

            "music_effect":
                mxmh.get("prediction_label"),

        }

    # ======================================================
    # COMPUTE OVERALL RISK
    # ======================================================

    def _compute_overall_risk(
        self,
        predictions: Dict[str, Any],
    ) -> str:
        """
        Compute overall mental-health risk from
        every prediction.
        """

        score = 0

        burnout = predictions.get(
            "burnout",
            {},
        ).get(
            "prediction_label",
            "",
        )

        if burnout == "High Burnout":
            score += 2

        elif burnout == "Moderate Burnout":
            score += 1

        wellness = predictions.get(
            "wellness",
            {},
        ).get(
            "prediction_label",
            "",
        )

        if wellness == "Poor Wellness":
            score += 2

        elif wellness == "Average Wellness":
            score += 1

        HIGH_RISK = {

            "high",

            "critical",

            "severe",

            "burnout",

            "poor",

            "distress",

        }

        MODERATE_RISK = {

            "moderate",

            "average",

            "medium",

            "borderline",

        }

        for model_name in [

            "mental_health_status",

            "student_survey",

            "stress_dataset",

        ]:

            label = str(

                predictions.get(
                    model_name,
                    {},
                ).get(
                    "prediction_label",
                    "",
                )

            ).lower()

            if any(word in label for word in HIGH_RISK):

                score += 2

            elif any(word in label for word in MODERATE_RISK):

                score += 1

        if score >= 8:
            return "High"

        if score >= 4:
            return "Moderate"

        return "Low"
    
    # ==========================================================
# SINGLETON
# ==========================================================

ai_model_service = AIModelService()


# ==========================================================
# PUBLIC PREDICTION API
# ==========================================================

def predict_user_assessment(
    profile_answers: Dict[str, Any],
    assessment_answers: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Main prediction API used by ml_engine.py.

    Steps
    -----
    1. Merge profile & assessment answers
    2. Build model-wise feature dictionaries
    3. Run prediction pipeline
    4. Return prediction bundle
    """

    merged_input = {}

    if profile_answers:
        merged_input.update(profile_answers)

    if assessment_answers:
        merged_input.update(assessment_answers)

    # ------------------------------------------------------
    # Build Features
    # ------------------------------------------------------

    model_inputs = build_all_model_inputs(
    profile_answers=profile_answers,
    assessment_answers=assessment_answers,
    )

    # ------------------------------------------------------
    # Run Prediction Pipeline
    # ------------------------------------------------------

    prediction_result = ai_model_service.predict_all(
        model_inputs,
    )

    # Optional debugging

    prediction_result["model_inputs"] = model_inputs

    return make_json_safe(
        prediction_result,
    )


# ==========================================================
# RELOAD AI MODELS
# ==========================================================

def reload_ai_models() -> Dict[str, Any]:
    """
    Reload all trained models without restarting Django.
    """

    ai_model_service.reload_models()

    return {

        "success": True,

        "message": "AI models reloaded successfully.",

    }


# ==========================================================
# AI MODEL STATUS
# ==========================================================

def get_ai_model_status() -> Dict[str, Any]:
    """
    Return current loading status of every AI model.
    """

    return ai_model_service.get_model_status()