"""
ai_model.py

Central AI Prediction Service for Calmify AI

Responsibilities
----------------
1. Load trained ML models
2. Load feature columns
3. Load label encoders
4. Predict every model
5. Build combined summary
6. Public prediction API
"""

"""
ai_model.py

Central AI Prediction Service for Calmify AI

Responsibilities
----------------
1. Load trained ML models
2. Load feature columns
3. Load label encoders
4. Predict using all trained models
5. Build combined mental health summary
6. Public API for ml_engine.py

Compatible with:
    ✓ feature_builder.py
    ✓ model_feature_mapper.py
    ✓ ml_engine.py
    ✓ views.py
"""

# ==========================================================
# IMPORTS
# ==========================================================

import json
import logging
from pathlib import Path
from typing import Any
from typing import Any, Dict, List, Optional
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
# AI MODEL SERVICE
# ==========================================================

class AIModelService:
    """
    Central Prediction Service.

    Responsible for:

    • Loading trained models
    • Loading feature columns
    • Loading label encoders
    • Running predictions
    • Returning combined mental health assessment
    """

    def __init__(self):
        """
        Initialise AI model service.
        """

        # Loaded sklearn/xgboost models
        self.models = {}

        # Feature column list for every model
        self.feature_columns = {}

        # Label encoders (if any)
        self.label_encoders = {}

        logger.info("Initializing AIModelService...")

        # Automatically load all trained models
        self.load_models()
        
            # ==========================================================
    # LOAD FEATURE COLUMNS
    # ==========================================================

    def _load_feature_columns(self, model_key):
        """
        Load feature columns used during training.
        """

        filename = FEATURE_COLUMNS_FILE_MAP.get(model_key)

        if filename is None:
            return None

        file_path = MODEL_DIR / filename

        if not file_path.exists():

            logger.warning(
                "Feature file not found: %s",
                file_path,
            )

            return None

        try:

            if file_path.suffix.lower() == ".json":

                with open(file_path, "r", encoding="utf-8") as file:
                    columns = json.load(file)

            else:

                columns = joblib.load(file_path)

            if isinstance(columns, pd.Index):
                columns = columns.tolist()

            elif not isinstance(columns, list):
                columns = list(columns)

            logger.info(
                "Loaded %d feature columns for %s",
                len(columns),
                model_key,
            )

            return columns

        except Exception:

            logger.exception(
                "Failed loading feature columns for %s",
                model_key,
            )

            return None


    # ==========================================================
    # LOAD LABEL ENCODER
    # ==========================================================

    def _load_label_encoder(self, model_key):
        """
        Load LabelEncoder if available.
        """

        filename = LABEL_ENCODER_FILE_MAP.get(model_key)

        if filename is None:
            return None

        file_path = MODEL_DIR / filename

        if not file_path.exists():

            logger.warning(
                "Label encoder not found: %s",
                file_path,
            )

            return None

        try:

            encoder = joblib.load(file_path)

            logger.info(
                "Loaded label encoder for %s",
                model_key,
            )

            return encoder

        except Exception:

            logger.exception(
                "Failed loading label encoder for %s",
                model_key,
            )

            return None


    # ==========================================================
    # LOAD MODELS
    # ==========================================================

    def load_models(self):
        """
        Load every trained model defined in TRAINED_MODEL_KEYS.
        """

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
                    "Model not found: %s",
                    model_path,
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
                    "Failed loading model %s",
                    model_key,
                )


    # ==========================================================
    # RELOAD MODELS
    # ==========================================================

    def reload_models(self):
        """
        Reload every trained model.
        """

        self.load_models()

        logger.info("All models reloaded successfully.")

        return True


    # ==========================================================
    # MODEL STATUS
    # ==========================================================

    def get_model_status(self):
        """
        Returns loading status of every model.
        """

        status = {}

        for model_key in TRAINED_MODEL_KEYS:

            status[model_key] = {

                "model_loaded":
                    model_key in self.models,

                "feature_columns_loaded":
                    self.feature_columns.get(model_key) is not None,

                "label_encoder_loaded":
                    self.label_encoders.get(model_key) is not None,

            }

        return status
    
        # ==========================================================
    # ALIGN FEATURES
    # ==========================================================

    def _align_features(
        self,
        model_key: str,
        features: dict,
    ) -> pd.DataFrame:
        """
        Align incoming features with the exact feature order
        used during model training.
        """

        feature_columns = self.feature_columns.get(model_key)

        # If feature file not available,
        # use raw feature dictionary.
        if feature_columns is None:
            return pd.DataFrame([features])

        aligned = {}

        for column in feature_columns:

            value = features.get(column, 0)

            if value is None:
                value = 0

            aligned[column] = value

        return pd.DataFrame([aligned])


    # ==========================================================
    # DECODE PREDICTION
    # ==========================================================

    def _decode_prediction(
        self,
        model_key: str,
        prediction,
    ):
        """
        Decode prediction using LabelEncoder if available.
        """

        encoder = self.label_encoders.get(model_key)

        if encoder is None:
            return prediction

        try:

            decoded = encoder.inverse_transform(
                np.array([prediction])
            )[0]

            return decoded

        except Exception:

            logger.exception(
                "Failed decoding prediction for %s",
                model_key,
            )

            return prediction


    # ==========================================================
    # SINGLE MODEL PREDICTION
    # ==========================================================

    def _predict_single_model(
        self,
        model_key: str,
        features: dict,
    ) -> dict:
        """
        Predict using one trained model.
        """

        if model_key not in self.models:

            raise RuntimeError(
                f"Model '{model_key}' is not loaded."
            )

        model = self.models[model_key]

        # ---------------------------------------------
        # Align features
        # ---------------------------------------------

        X = self._align_features(
            model_key,
            features,
        )

        # ---------------------------------------------
        # Prediction
        # ---------------------------------------------

        prediction = model.predict(X)[0]

        prediction = make_json_safe(prediction)

        prediction_label = self._decode_prediction(
            model_key,
            prediction,
        )

        result = {

            "prediction": prediction,

            "prediction_label": str(prediction_label),

            "features_used": features,

            "confidence": None,

            "probabilities": {},

        }

        # ---------------------------------------------
        # Prediction Probability
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
                        float(probability),
                        4,
                    )

                    for index, probability in enumerate(
                        probabilities
                    )

                }

            except Exception:

                logger.exception(
                    "Failed computing probability for %s",
                    model_key,
                )

        return make_json_safe(result)
    
        # ==========================================================
    # PREDICT ALL MODELS
    # ==========================================================

    def predict_all(
        self,
        model_inputs: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run prediction on all trained models.
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
            predictions
        )

        return {

            "success": len(predictions) > 0,

            "predictions": predictions,

            "combined_summary": combined_summary,

            "failed_models": failed_models,

        }
        
            # ==========================================================
    # BUILD COMBINED SUMMARY
    # ==========================================================

    def _build_combined_summary(
        self,
        predictions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Combine outputs of all models into one summary.
        """

        overall_risk = self._compute_overall_risk(
            predictions
        )

        return {

            "overall_risk_level": overall_risk,

            "burnout_level":
                predictions.get(
                    "burnout",
                    {}
                ).get(
                    "prediction_label",
                    "Unknown"
                ),

            "wellness_level":
                predictions.get(
                    "wellness",
                    {}
                ).get(
                    "prediction_label",
                    "Unknown"
                ),

            "mental_health_status":
                predictions.get(
                    "mental_health_status",
                    {}
                ).get(
                    "prediction_label",
                    "Unknown"
                ),

            "student_stress_level":
                predictions.get(
                    "student_survey",
                    {}
                ).get(
                    "prediction_label",
                    "Unknown"
                ),

            "stress_dataset_level":
                predictions.get(
                    "stress_dataset",
                    {}
                ).get(
                    "prediction_label",
                    "Unknown"
                ),

            # Rule-based engine ke liye reserved
            "music_effect_case1":
                predictions.get(
                    "mxmh_case1",
                    {}
                ).get(
                    "prediction_label",
                    "Not Evaluated"
                ),

            "music_effect_case2":
                predictions.get(
                    "mxmh_case2",
                    {}
                ).get(
                    "prediction_label",
                    "Unknown"
                ),

        }
        
            # ==========================================================
    # COMPUTE OVERALL RISK
    # ==========================================================

    def _compute_overall_risk(
        self,
        predictions: Dict[str, Any],
    ) -> str:
        """
        Compute overall mental health risk
        using all trained model outputs.
        """

        score = 0

        HIGH_RISK = {
            "high",
            "critical",
            "poor",
            "burnout",
            "severe",
            "extreme",
            "distress",
        }

        MODERATE_RISK = {
            "moderate",
            "medium",
            "average",
            "borderline",
        }

        LOW_RISK = {
            "healthy",
            "good",
            "normal",
            "low",
            "stable",
        }

        for result in predictions.values():

            if not isinstance(result, dict):
                continue

            label = str(
                result.get(
                    "prediction_label",
                    ""
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
    Main API used by ml_engine.py.
    """

    merged_input = {}

    if profile_answers:
        merged_input.update(profile_answers)

    if assessment_answers:
        merged_input.update(assessment_answers)

    # -----------------------------------------
    # Build model-wise feature dictionaries
    # -----------------------------------------

    model_inputs = build_all_model_inputs(
        merged_input
    )

    # -----------------------------------------
    # Run prediction pipeline
    # -----------------------------------------

    result = ai_model_service.predict_all(
        model_inputs
    )

    # Optional debugging
    result["model_inputs"] = model_inputs

    return make_json_safe(result)


# ==========================================================
# RELOAD MODELS
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
# MODEL STATUS
# ==========================================================

def get_ai_model_status() -> Dict[str, Any]:
    """
    Return loading status of every AI model.
    """

    return ai_model_service.get_model_status()