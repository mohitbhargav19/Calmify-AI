"""
feature_builder.py

Calmify AI
---------------------------------------

Responsible for building model-specific feature dictionaries
for every trained ML model.

Pipeline

Raw Profile + Assessment Answers
                │
                ▼
        FeatureBuilder
                │
                ▼
 Model-wise Feature Dictionaries
                │
                ▼
            ai_model.py

This module DOES NOT:

❌ Load ML models
❌ Perform predictions
❌ Scale data
❌ Encode using sklearn encoders

It ONLY prepares feature dictionaries.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

try:
    from mental_health.utils import make_json_safe
except ImportError:
    from .utils import make_json_safe

logger = logging.getLogger(__name__)

# ==========================================================
# MODEL KEYS
# ==========================================================

BURNOUT_MODEL = "burnout"

WELLNESS_MODEL = "wellness"

MENTAL_HEALTH_MODEL = "mental_health_status"

STUDENT_SURVEY_MODEL = "student_survey"

STRESS_DATASET_MODEL = "stress_dataset"

MXMH_CASE1_MODEL = "mxmh_case1"

MXMH_CASE2_MODEL = "mxmh_case2"

TRAINED_MODEL_KEYS = [

    BURNOUT_MODEL,

    WELLNESS_MODEL,

    MENTAL_HEALTH_MODEL,

    STUDENT_SURVEY_MODEL,

    STRESS_DATASET_MODEL,

    MXMH_CASE1_MODEL,

    MXMH_CASE2_MODEL,

]

# ==========================================================
# DEFAULT VALUES
# ==========================================================

DEFAULT_NUMERIC = 0.0

DEFAULT_INTEGER = 0

DEFAULT_STRING = ""

DEFAULT_BOOLEAN = False

# ==========================================================
# GENDER ENCODING
# ==========================================================

GENDER_MAP = {

    "male": 0,

    "female": 1,

    "other": 2,

}

# ==========================================================
# YES / NO ENCODING
# ==========================================================

YES_NO_MAP = {

    "yes": 1,

    "true": 1,

    "y": 1,

    "1": 1,

    "no": 0,

    "false": 0,

    "n": 0,

    "0": 0,

}

# ==========================================================
# MUSIC EFFECT ENCODING
# ==========================================================

MUSIC_EFFECT_MAP = {

    "worsen": 0,

    "no effect": 1,

    "improve": 2,

}

# ==========================================================
# STRESS LABEL ENCODING
# ==========================================================

STRESS_LABEL_MAP = {

    "low": 0,

    "moderate": 1,

    "high": 2,

}

# ==========================================================
# MUSIC GENRE ENCODING
# (Must stay compatible with MXMH notebooks)
# ==========================================================

GENRE_MAP = {

    "classical": 0,

    "lofi": 1,

    "pop": 2,

    "rock": 3,

    "hip hop": 4,

    "jazz": 5,

    "electronic": 6,

    "edm": 7,

    "rap": 8,

    "country": 9,

    "metal": 10,

    "folk": 11,

    "blues": 12,

    "r&b": 13,

    "indie": 14,

}

# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [

    "FeatureBuilder",

    "build_all_model_inputs",

]

# ==========================================================
# FEATURE BUILDER
# ==========================================================

class FeatureBuilder:
    """
    Builds model-specific feature dictionaries for every
    trained Calmify AI model.

    Parameters
    ----------
    profile_answers : dict
        User profile collected during signup.

    assessment_answers : dict
        Assessment questionnaire responses.
    """

    def __init__(
        self,
        profile_answers: Dict[str, Any],
        assessment_answers: Dict[str, Any],
    ) -> None:

        self.profile = profile_answers or {}

        self.assessment = assessment_answers or {}

    # ======================================================
    # SAFE GETTERS
    # ======================================================

    def _get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Searches assessment first,
        then profile,
        otherwise returns default.
        """

        if key in self.assessment:
            return self.assessment.get(key)

        if key in self.profile:
            return self.profile.get(key)

        return default

    def _get_string(
        self,
        key: str,
        default: str = DEFAULT_STRING,
    ) -> str:

        value = self._get(key, default)

        if value is None:
            return default

        return str(value).strip()

    def _get_lower(
        self,
        key: str,
        default: str = DEFAULT_STRING,
    ) -> str:

        return self._get_string(
            key,
            default,
        ).lower()

    def _get_float(
        self,
        key: str,
        default: float = DEFAULT_NUMERIC,
    ) -> float:

        value = self._get(key)

        try:
            return float(value)

        except (TypeError, ValueError):
            return default

    def _get_int(
        self,
        key: str,
        default: int = DEFAULT_INTEGER,
    ) -> int:

        value = self._get(key)

        try:
            return int(float(value))

        except (TypeError, ValueError):
            return default

    def _get_bool(
        self,
        key: str,
        default: bool = DEFAULT_BOOLEAN,
    ) -> bool:

        value = self._get(key)

        if isinstance(value, bool):
            return value

        value = str(value).strip().lower()

        if value in YES_NO_MAP:
            return bool(YES_NO_MAP[value])

        return default

    # ======================================================
    # ENCODERS
    # ======================================================

    def _encode_gender(self) -> int:
        """
        Encodes gender using GENDER_MAP.
        """

        gender = self._get_lower("gender")

        return GENDER_MAP.get(gender, 2)

    def _encode_genre(self) -> int:
        """
        Encodes favourite music genre.
        """

        genre = (
            self._get_lower("favorite_genre")
            or self._get_lower("fav_genre")
            or self._get_lower("music_genre")
        )

        return GENRE_MAP.get(genre, 0)

    def _encode_music_effect(self) -> int:
        """
        Encodes expected music effect.
        """

        effect = self._get_lower("music_effect")

        return MUSIC_EFFECT_MAP.get(effect, 1)

    def _encode_stress_label(self) -> int:
        """
        Encodes stress label.
        """

        label = self._get_lower("stress_level_label")

        return STRESS_LABEL_MAP.get(label, 1)
    
    
        # ======================================================
    # COMMON DERIVED FEATURES
    # ======================================================

    def _sleep_balance_score(self) -> float:
        """
        Returns a normalized sleep quality score (0–10).
        """

        sleep_hours = self._get_float("sleep_hours")

        if sleep_hours <= 0:
            return 5.0

        if sleep_hours >= 8:
            return 10.0

        if sleep_hours >= 7:
            return 8.5

        if sleep_hours >= 6:
            return 7.0

        if sleep_hours >= 5:
            return 5.0

        return 2.5

    def _digital_overload_score(self) -> float:
        """
        Screen-time overload score (0–10).
        Higher = more overload.
        """

        screen_time = (
            self._get_float("screen_time")
            or self._get_float("screen_time_hours")
            or self._get_float("internet_usage")
        )

        if screen_time <= 0:
            return 0.0

        return min(screen_time, 10.0)

    def _study_load_score(self) -> float:
        """
        Combines study hours and exam pressure.
        """

        study_hours = self._get_float("study_hours_per_day")
        exam_pressure = self._get_float("exam_pressure")

        return round(
            (study_hours * 0.4) +
            (exam_pressure * 0.6),
            2,
        )

    def _stress_pressure_score(self) -> float:
        """
        Overall perceived stress score.
        """

        stress = self._get_float("stress_level")
        anxiety = self._get_float("anxiety_score")
        depression = self._get_float("depression_score")

        values = [stress, anxiety, depression]

        values = [v for v in values if v > 0]

        if not values:
            return 0.0

        return round(sum(values) / len(values), 2)

    def _lifestyle_support_score(self) -> float:
        """
        Lifestyle quality score.

        Higher = healthier lifestyle.
        """

        physical = self._get_float("physical_activity")
        social = self._get_float("social_support")

        sleep = self._sleep_balance_score()

        return round(
            (physical + social + sleep) / 3,
            2,
        )

    def _sleep_deficit(self) -> float:
        """
        Hours below ideal sleep (8h).
        """

        sleep = self._get_float("sleep_hours")

        if sleep <= 0:
            return 0.0

        return max(0.0, 8.0 - sleep)

    def _caffeine_burden(self) -> float:
        """
        Estimates caffeine burden.

        Accepts either:
            caffeine
            caffeine_intake
            coffee_per_day
        """

        caffeine = (
            self._get_float("caffeine")
            or self._get_float("caffeine_intake")
            or self._get_float("coffee_per_day")
        )

        return min(caffeine, 10.0)

    def _overall_wellness_index(self) -> float:
        """
        Composite wellness indicator.

        Combines:

        • Sleep
        • Lifestyle
        • Stress

        Higher = healthier.
        """

        sleep = self._sleep_balance_score()

        lifestyle = self._lifestyle_support_score()

        stress = self._stress_pressure_score()

        wellness = (
            (sleep * 0.35)
            + (lifestyle * 0.40)
            + ((10 - stress) * 0.25)
        )

        return round(
            max(0.0, min(10.0, wellness)),
            2,
        )
        
        
            # ============================================================
    # Burnout Regression Features
    # ============================================================

    def build_burnout_features(self) -> Dict[str, Any]:
        """
        Build feature dictionary for the Burnout Regression model.

        Returns
        -------
        Dict[str, Any]
            Feature dictionary aligned with burnout_feature_columns.pkl
        """

        features = {

            # --------------------------------------------------
            # Academic / Workload
            # --------------------------------------------------

            "study_hours_per_day":
                self._get_float("study_hours_per_day"),

            "exam_pressure":
                self._get_float("exam_pressure"),

            "academic_workload":
                self._study_load_score(),

            "stress_level":
                self._get_float("stress_level"),

            "stress_pressure":
                self._stress_pressure_score(),

            # --------------------------------------------------
            # Lifestyle
            # --------------------------------------------------

            "sleep_hours":
                self._get_float("sleep_hours"),

            "sleep_balance":
                self._sleep_balance_score(),

            "sleep_deficit":
                self._sleep_deficit(),

            "screen_time":
                self._get_float("screen_time"),

            "digital_overload":
                self._digital_overload_score(),

            "physical_activity":
                self._get_float("physical_activity"),

            "lifestyle_support":
                self._lifestyle_support_score(),

            "social_support":
                self._get_float("social_support"),

            # --------------------------------------------------
            # Emotional Indicators
            # --------------------------------------------------

            "anxiety_score":
                self._get_float("anxiety_score"),

            "depression_score":
                self._get_float("depression_score"),

            "mental_fatigue":
                self._get_float("mental_fatigue"),

            "motivation_level":
                self._get_float("motivation_level"),

            # --------------------------------------------------
            # Behaviour
            # --------------------------------------------------

            "internet_usage":
                self._get_float("internet_usage"),

            "caffeine_intake":
                self._get_float("caffeine_intake"),

            "caffeine_burden":
                self._caffeine_burden(),

            # --------------------------------------------------
            # Profile
            # --------------------------------------------------

            "age":
                self._get_int("age"),

            "gender":
                self._encode_gender(),

            "academic_year":
                self._get_int("academic_year"),

            # --------------------------------------------------
            # Derived Wellness
            # --------------------------------------------------

            "overall_wellness_index":
                self._overall_wellness_index(),
        }

        return make_json_safe(features)
    
        # ============================================================
    # Wellness Regression Features
    # ============================================================

    def build_wellness_features(self) -> Dict[str, Any]:
        """
        Build feature dictionary for the Wellness Regression model.

        Returns
        -------
        Dict[str, Any]
            Feature dictionary aligned with wellness_feature_columns.pkl
        """

        features = {

            # --------------------------------------------------
            # Lifestyle
            # --------------------------------------------------

            "sleep_hours":
                self._get_float("sleep_hours"),

            "sleep_balance":
                self._sleep_balance_score(),

            "sleep_deficit":
                self._sleep_deficit(),

            "physical_activity":
                self._get_float("physical_activity"),

            "social_support":
                self._get_float("social_support"),

            "lifestyle_support":
                self._lifestyle_support_score(),

            "overall_wellness_index":
                self._overall_wellness_index(),

            # --------------------------------------------------
            # Mental State
            # --------------------------------------------------

            "stress_level":
                self._get_float("stress_level"),

            "stress_pressure":
                self._stress_pressure_score(),

            "anxiety_score":
                self._get_float("anxiety_score"),

            "depression_score":
                self._get_float("depression_score"),

            "motivation_level":
                self._get_float("motivation_level"),

            "mental_fatigue":
                self._get_float("mental_fatigue"),

            # --------------------------------------------------
            # Academic Balance
            # --------------------------------------------------

            "study_hours_per_day":
                self._get_float("study_hours_per_day"),

            "exam_pressure":
                self._get_float("exam_pressure"),

            "academic_workload":
                self._study_load_score(),

            # --------------------------------------------------
            # Digital Behaviour
            # --------------------------------------------------

            "screen_time":
                self._get_float("screen_time"),

            "digital_overload":
                self._digital_overload_score(),

            "internet_usage":
                self._get_float("internet_usage"),

            # --------------------------------------------------
            # Nutrition / Stimulants
            # --------------------------------------------------

            "caffeine_intake":
                self._get_float("caffeine_intake"),

            "caffeine_burden":
                self._caffeine_burden(),

            # --------------------------------------------------
            # Profile
            # --------------------------------------------------

            "age":
                self._get_int("age"),

            "gender":
                self._encode_gender(),

            "academic_year":
                self._get_int("academic_year"),
        }

        return make_json_safe(features)
    
        # ============================================================
    # Mental Health Status Classification Features
    # ============================================================

    def build_mental_health_features(self) -> Dict[str, Any]:
        """
        Build feature dictionary for the Mental Health Status
        classification model.

        Returns
        -------
        Dict[str, Any]
            Feature dictionary aligned with
            mental_health_feature_columns.pkl
        """

        features = {

            # --------------------------------------------------
            # Demographics
            # --------------------------------------------------

            "age":
                self._get_int("age"),

            "gender":
                self._encode_gender(),

            "academic_year":
                self._get_int("academic_year"),

            # --------------------------------------------------
            # Academic
            # --------------------------------------------------

            "study_hours_per_day":
                self._get_float("study_hours_per_day"),

            "exam_pressure":
                self._get_float("exam_pressure"),

            "academic_workload":
                self._study_load_score(),

            # --------------------------------------------------
            # Mental State
            # --------------------------------------------------

            "stress_level":
                self._get_float("stress_level"),

            "stress_pressure":
                self._stress_pressure_score(),

            "anxiety_score":
                self._get_float("anxiety_score"),

            "depression_score":
                self._get_float("depression_score"),

            "mental_fatigue":
                self._get_float("mental_fatigue"),

            "motivation_level":
                self._get_float("motivation_level"),

            # --------------------------------------------------
            # Lifestyle
            # --------------------------------------------------

            "sleep_hours":
                self._get_float("sleep_hours"),

            "sleep_balance":
                self._sleep_balance_score(),

            "sleep_deficit":
                self._sleep_deficit(),

            "physical_activity":
                self._get_float("physical_activity"),

            "social_support":
                self._get_float("social_support"),

            "lifestyle_support":
                self._lifestyle_support_score(),

            "overall_wellness_index":
                self._overall_wellness_index(),

            # --------------------------------------------------
            # Digital Behaviour
            # --------------------------------------------------

            "screen_time":
                self._get_float("screen_time"),

            "digital_overload":
                self._digital_overload_score(),

            "internet_usage":
                self._get_float("internet_usage"),

            # --------------------------------------------------
            # Stimulants
            # --------------------------------------------------

            "caffeine_intake":
                self._get_float("caffeine_intake"),

            "caffeine_burden":
                self._caffeine_burden(),
        }

        return make_json_safe(features)
    
        # ============================================================
    # Student Mental Health Survey Classification Features
    # ============================================================

    def build_student_survey_features(self) -> Dict[str, Any]:
        """
        Build feature dictionary for the Student Mental Health
        Survey classifier.

        Returns
        -------
        Dict[str, Any]
            Feature dictionary aligned with
            student_survey_feature_columns.pkl
        """

        features = {

            # --------------------------------------------------
            # Demographics
            # --------------------------------------------------

            "age":
                self._get_int("age"),

            "gender":
                self._encode_gender(),

            "academic_year":
                self._get_int("academic_year"),

            # --------------------------------------------------
            # Academic
            # --------------------------------------------------

            "study_hours_per_day":
                self._get_float("study_hours_per_day"),

            "exam_pressure":
                self._get_float("exam_pressure"),

            "academic_workload":
                self._study_load_score(),

            "academic_performance":
                self._get_float("academic_performance"),

            # --------------------------------------------------
            # Emotional Health
            # --------------------------------------------------

            "stress_level":
                self._get_float("stress_level"),

            "stress_pressure":
                self._stress_pressure_score(),

            "anxiety_score":
                self._get_float("anxiety_score"),

            "depression_score":
                self._get_float("depression_score"),

            "mental_fatigue":
                self._get_float("mental_fatigue"),

            "motivation_level":
                self._get_float("motivation_level"),

            # --------------------------------------------------
            # Lifestyle
            # --------------------------------------------------

            "sleep_hours":
                self._get_float("sleep_hours"),

            "sleep_balance":
                self._sleep_balance_score(),

            "sleep_deficit":
                self._sleep_deficit(),

            "physical_activity":
                self._get_float("physical_activity"),

            "social_support":
                self._get_float("social_support"),

            "lifestyle_support":
                self._lifestyle_support_score(),

            "overall_wellness_index":
                self._overall_wellness_index(),

            # --------------------------------------------------
            # Digital Behaviour
            # --------------------------------------------------

            "screen_time":
                self._get_float("screen_time"),

            "digital_overload":
                self._digital_overload_score(),

            "internet_usage":
                self._get_float("internet_usage"),

            # --------------------------------------------------
            # Family / Financial
            # --------------------------------------------------

            "family_expectation":
                self._get_float("family_expectation"),

            "financial_stress":
                self._get_float("financial_stress"),

            # --------------------------------------------------
            # Stimulants
            # --------------------------------------------------

            "caffeine_intake":
                self._get_float("caffeine_intake"),

            "caffeine_burden":
                self._caffeine_burden(),
        }

        return make_json_safe(features)
    
        # ============================================================
    # Stress Dataset Classification Features
    # ============================================================

    def build_stress_dataset_features(self) -> Dict[str, Any]:
        """
        Build feature dictionary for the Stress Level Dataset
        classification model.

        Returns
        -------
        Dict[str, Any]
            Feature dictionary aligned with
            stress_dataset_feature_columns.pkl
        """

        features = {

            # --------------------------------------------------
            # Demographics
            # --------------------------------------------------

            "age":
                self._get_int("age"),

            "gender":
                self._encode_gender(),

            # --------------------------------------------------
            # Core Stress Indicators
            # --------------------------------------------------

            "stress_level":
                self._get_float("stress_level"),

            "stress_pressure":
                self._stress_pressure_score(),

            "recent_stress":
                self._get_float("recent_stress"),

            # --------------------------------------------------
            # Emotional Indicators
            # --------------------------------------------------

            "anxiety_score":
                self._get_float("anxiety_score"),

            "depression_score":
                self._get_float("depression_score"),

            "sadness":
                self._get_float("sadness"),

            "irritability":
                self._get_float("irritability"),

            "loneliness":
                self._get_float("loneliness"),

            "confidence_issues":
                self._get_float("confidence_issues"),

            "concentration_issues":
                self._get_float("concentration_issues"),

            # --------------------------------------------------
            # Physiological Symptoms
            # --------------------------------------------------

            "rapid_heartbeat":
                self._get_float("rapid_heartbeat"),

            "headaches":
                self._get_float("headaches"),

            "mental_fatigue":
                self._get_float("mental_fatigue"),

            # --------------------------------------------------
            # Lifestyle
            # --------------------------------------------------

            "sleep_hours":
                self._get_float("sleep_hours"),

            "sleep_balance":
                self._sleep_balance_score(),

            "sleep_deficit":
                self._sleep_deficit(),

            "physical_activity":
                self._get_float("physical_activity"),

            "social_support":
                self._get_float("social_support"),

            "lifestyle_support":
                self._lifestyle_support_score(),

            "overall_wellness_index":
                self._overall_wellness_index(),

            # --------------------------------------------------
            # Academic
            # --------------------------------------------------

            "study_hours_per_day":
                self._get_float("study_hours_per_day"),

            "exam_pressure":
                self._get_float("exam_pressure"),

            "academic_overwhelm":
                self._get_float("academic_overwhelm"),

            "academic_workload":
                self._study_load_score(),

            # --------------------------------------------------
            # Behaviour
            # --------------------------------------------------

            "screen_time":
                self._get_float("screen_time"),

            "digital_overload":
                self._digital_overload_score(),

            "internet_usage":
                self._get_float("internet_usage"),

            "leisure_difficulty":
                self._get_float("leisure_difficulty"),

            # --------------------------------------------------
            # Stimulants
            # --------------------------------------------------

            "caffeine_intake":
                self._get_float("caffeine_intake"),

            "caffeine_burden":
                self._caffeine_burden(),
        }

        return make_json_safe(features)
    
        # ============================================================
    # MXMH (Music x Mental Health) Features
    # ============================================================

    def build_mxmh_features(self) -> Dict[str, Any]:
        """
        Build feature dictionary for both:

        • MXMH Case 1 (Genre Recommendation)
        • MXMH Case 2 (Music Effect Prediction)

        Returns
        -------
        Dict[str, Any]
            Feature dictionary aligned with
            mxmh_case1_feature_columns.pkl
            mxmh_case2_feature_columns.pkl
        """

        features = {

            # --------------------------------------------------
            # Demographics
            # --------------------------------------------------

            "age":
                self._get_int("age"),

            "gender":
                self._encode_gender(),

            # --------------------------------------------------
            # Music Behaviour
            # --------------------------------------------------

            "favorite_genre":
                self._encode_genre(),

            "hours_per_day":
                self._get_float("hours_per_day"),

            "while_working":
                self._get_bool("while_working"),

            "exploratory":
                self._get_bool("exploratory"),

            "foreign_languages":
                self._get_bool("foreign_languages"),

            "instrumentalist":
                self._get_bool("instrumentalist"),

            "composer":
                self._get_bool("composer"),

            # --------------------------------------------------
            # Mental Health Scores
            # --------------------------------------------------

            "anxiety_score":
                self._get_float("anxiety_score"),

            "depression_score":
                self._get_float("depression_score"),

            "stress_level":
                self._get_float("stress_level"),

            "stress_pressure":
                self._stress_pressure_score(),

            # --------------------------------------------------
            # Sleep
            # --------------------------------------------------

            "sleep_hours":
                self._get_float("sleep_hours"),

            "sleep_balance":
                self._sleep_balance_score(),

            "sleep_deficit":
                self._sleep_deficit(),

            "insomnia":
                self._get_float("insomnia"),

            # --------------------------------------------------
            # Mental Conditions
            # --------------------------------------------------

            "ocd":
                self._get_float("ocd"),

            "mental_fatigue":
                self._get_float("mental_fatigue"),

            "motivation_level":
                self._get_float("motivation_level"),

            # --------------------------------------------------
            # Lifestyle
            # --------------------------------------------------

            "physical_activity":
                self._get_float("physical_activity"),

            "social_support":
                self._get_float("social_support"),

            "overall_wellness_index":
                self._overall_wellness_index(),

            # --------------------------------------------------
            # Digital Behaviour
            # --------------------------------------------------

            "screen_time":
                self._get_float("screen_time"),

            "digital_overload":
                self._digital_overload_score(),

            # --------------------------------------------------
            # Academic
            # --------------------------------------------------

            "study_hours_per_day":
                self._get_float("study_hours_per_day"),

            "exam_pressure":
                self._get_float("exam_pressure"),

            "academic_workload":
                self._study_load_score(),
        }

        return make_json_safe(features)
    
        # ============================================================
    # Public API
    # ============================================================

    def build_all_model_inputs(self) -> Dict[str, Dict[str, Any]]:
        """
        Build feature dictionaries for every ML model.

        This is the only public method that ai_model.py should use.

        Returns
        -------
        Dict[str, Dict[str, Any]]
        """

        model_inputs = {

            BURNOUT_MODEL:
                self.build_burnout_features(),

            WELLNESS_MODEL:
                self.build_wellness_features(),

            MENTAL_HEALTH_MODEL:
                self.build_mental_health_features(),

            STUDENT_SURVEY_MODEL:
                self.build_student_survey_features(),

            STRESS_DATASET_MODEL:
                self.build_stress_dataset_features(),

            MXMH_CASE1_MODEL:
                self.build_mxmh_features(),

            MXMH_CASE2_MODEL:
                self.build_mxmh_features(),
        }

        return make_json_safe(model_inputs)
    
    # ============================================================
# Singleton
# ============================================================

# feature_builder = FeatureBuilder()


# ============================================================
# Public Function
# ============================================================

def build_all_model_inputs(
    profile_answers,
    assessment_answers,
):
    builder = FeatureBuilder(
        profile_answers=profile_answers,
        assessment_answers=assessment_answers,
    )

    return builder.build_all_model_inputs()