from __future__ import annotations

import logging
import math
from typing import Any, Dict

from rest_framework import serializers

logger = logging.getLogger(__name__)

# ============================================================
# CONSTANTS
# ============================================================

MAX_TEXT_LENGTH = 5000

MIN_AGE = 15
MAX_AGE = 40

MIN_ACADEMIC_YEAR = 1
MAX_ACADEMIC_YEAR = 8

# ============================================================
# VALID CHOICES
# ============================================================

VALID_GENDERS = {
    "male",
    "female",
    "other",
}

VALID_BOOLEAN = {
    "yes",
    "no",
    "true",
    "false",
    "1",
    "0",
}

VALID_MUSIC_EFFECT = {
    "improve",
    "no effect",
    "worsen",
}

VALID_GENRES = {
    "classical",
    "country",
    "edm",
    "folk",
    "gospel",
    "hip hop",
    "jazz",
    "k pop",
    "latin",
    "lofi",
    "metal",
    "pop",
    "r&b",
    "rap",
    "rock",
    "video game music",
    "instrumental",
    "ambient",
    "other",
}

VALID_YES_NO = {
    "yes",
    "no",
}

# ============================================================
# SHARABLE NORMALIZATION HELPER
# ============================================================

class Normalizer:
    """
    Shared normalization helper.
    """

    @staticmethod
    def string(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def lower(value: Any) -> str:
        return Normalizer.string(value).lower()

    @staticmethod
    def integer(value: Any, default=None):
        if value in ("", None):
            return default
        try:
            return int(float(value))
        except Exception:
            return default

    @staticmethod
    def number(value: Any, default=0.0):
        if value in ("", None):
            return default
        try:
            return float(value)
        except Exception:
            return default

    @staticmethod
    def float_value(value, default=0.0):
        try:
            if value in ("", None):
                return float(default)
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    @staticmethod
    def int_value(value, default=0):
        try:
            if value in ("", None):
                return int(default)
            return int(float(value))
        except (TypeError, ValueError):
            return int(default)

    @staticmethod
    def boolean(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        value = Normalizer.lower(value)
        return value in {"yes", "true", "1", "y", "on"}

    @staticmethod
    def bool_value(value):
        if isinstance(value, bool):
            return value
        value = Normalizer.lower(value)
        return value in {"yes", "true", "1", "y", "t", "on"}

    @staticmethod
    def list_value(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @staticmethod
    def dict_value(value):
        if isinstance(value, dict):
            return value
        return {}

    @staticmethod
    def remove_none(data):
        if isinstance(data, dict):
            return {
                key: Normalizer.remove_none(val)
                for key, val in data.items()
                if val is not None
            }
        if isinstance(data, list):
            return [
                Normalizer.remove_none(item)
                for item in data
                if item is not None
            ]
        return data

    @staticmethod
    def safe_json(value):
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return 0.0
            return value
        if isinstance(value, dict):
            return {k: Normalizer.safe_json(v) for k, v in value.items()}
        if isinstance(value, list):
            return [Normalizer.safe_json(v) for v in value]
        return value

    @staticmethod
    def json_safe(data):
        return Normalizer.safe_json(data)


NormalizationHelper = Normalizer

# ============================================================
# PROFILE SERIALIZER
# ============================================================

class ProfileSerializer(serializers.Serializer):
    """
    Validates profile data received from assessment.js.
    """

    age = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=MIN_AGE,
        max_value=MAX_AGE,
    )

    gender = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    academic_year = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=MIN_ACADEMIC_YEAR,
        max_value=MAX_ACADEMIC_YEAR,
    )

    course = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    college = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    city = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate_gender(self, value):
        gender = Normalizer.lower(value)
        if gender == "":
            return "other"
        if gender not in VALID_GENDERS:
            raise serializers.ValidationError(
                f"Gender must be one of {sorted(VALID_GENDERS)}."
            )
        return gender

    def validate_course(self, value):
        return Normalizer.string(value)

    def validate_college(self, value):
        return Normalizer.string(value)

    def validate_city(self, value):
        return Normalizer.string(value)

    def validate(self, attrs):
        attrs.setdefault("age", None)
        attrs.setdefault("gender", "other")
        attrs.setdefault("academic_year", None)
        attrs.setdefault("course", "")
        attrs.setdefault("college", "")
        attrs.setdefault("city", "")
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "age": Normalizer.integer(data.get("age"), None),
            "gender": Normalizer.lower(data.get("gender")),
            "academic_year": Normalizer.integer(data.get("academic_year"), None),
            "course": Normalizer.string(data.get("course")),
            "college": Normalizer.string(data.get("college")),
            "city": Normalizer.string(data.get("city")),
        }

# ============================================================
# ASSESSMENT SERIALIZER
# ============================================================

class AssessmentSerializer(serializers.Serializer):
    """
    Validates assessment answers submitted from assessment.js.
    Uses CharField for numeric inputs to clean empty values cleanly.
    """

    journal_text = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=MAX_TEXT_LENGTH,
    )

    # ========================================================
    # Lifestyle (Updated to CharField)
    # ========================================================
    sleep_hours = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    screen_time = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    study_hours = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    physical_activity = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    social_support = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    caffeine_intake = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # ========================================================
    # Academic (Updated to CharField)
    # ========================================================
    stress_level = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    exam_pressure = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_performance = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    financial_stress = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_expectation = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # ========================================================
    # Mental Health (Updated to CharField)
    # ========================================================
    anxiety_score = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    depression_score = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recent_stress = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rapid_heartbeat = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    headaches = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    irritability = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    concentration_issues = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sadness = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    loneliness = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_overwhelm = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    leisure_difficulty = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    confidence_issues = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # ========================================================
    # Music & Behaviour
    # ========================================================
    favorite_genre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    hours_per_day_music = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    while_working = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    exploratory = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    foreign_languages = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instrumentalist = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    composer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    insomnia = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ocd = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    music_effect = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def _normalize_numeric_fields(self, attrs):
        numeric_fields = [
            "sleep_hours", "screen_time", "study_hours", "physical_activity",
            "social_support", "caffeine_intake", "stress_level", "exam_pressure",
            "academic_performance", "financial_stress", "family_expectation",
            "anxiety_score", "depression_score", "recent_stress", "rapid_heartbeat",
            "headaches", "irritability", "concentration_issues", "sadness",
            "loneliness", "academic_overwhelm", "leisure_difficulty", "confidence_issues",
            "hours_per_day_music", "insomnia", "ocd"
        ]
        for field in numeric_fields:
            if field in attrs:
                attrs[field] = Normalizer.float_value(attrs.get(field), 0.0)
        return attrs

    def _validate_yes_no(self, value):
        if value is None:
            return "no"
        value = Normalizer.lower(value)
        if value not in VALID_YES_NO:
            raise serializers.ValidationError(f"Value must be one of: {sorted(VALID_YES_NO)}")
        return value

    def validate_favorite_genre(self, value):
        value = Normalizer.lower(value)
        if value not in VALID_GENRES:
            return "other"
        return value

    def validate_music_effect(self, value):
        value = Normalizer.lower(value)
        if value not in VALID_MUSIC_EFFECT:
            return "no effect"
        return value

    def validate_while_working(self, value):
        return self._validate_yes_no(value)

    def validate_exploratory(self, value):
        return self._validate_yes_no(value)

    def validate_foreign_languages(self, value):
        return self._validate_yes_no(value)

    def validate_instrumentalist(self, value):
        return self._validate_yes_no(value)

    def validate_composer(self, value):
        return self._validate_yes_no(value)

    def validate(self, attrs):
        attrs = self._normalize_numeric_fields(attrs)
        attrs["journal_text"] = Normalizer.string(attrs.get("journal_text"))
        return attrs

    def to_representation(self, instance):
        return dict(super().to_representation(instance))

# ============================================================
# COMBINED ASSESSMENT SERIALIZER
# ============================================================

class CombinedAssessmentSerializer(serializers.Serializer):
    """
    Main serializer used by AssessmentSubmitView.
    """

    profile = ProfileSerializer(required=True)
    assessment = AssessmentSerializer(required=True)

    def validate(self, attrs):
        profile = attrs.get("profile") or {}
        assessment = attrs.get("assessment") or {}
        return {
            "profile": profile,
            "assessment": assessment,
        }

    @property
    def profile_data(self):
        if not hasattr(self, "validated_data"):
            return {}
        return self.validated_data.get("profile", {})

    @property
    def assessment_data(self):
        if not hasattr(self, "validated_data"):
            return {}
        return self.validated_data.get("assessment", {})

    def build_feature_builder_payload(self):
        return {
            "profile_answers": dict(self.profile_data),
            "assessment_answers": dict(self.assessment_data),
        }

    def build_dashboard_payload(self):
        return {
            "profile": dict(self.profile_data),
            "assessment": dict(self.assessment_data),
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            "profile": representation.get("profile", {}),
            "assessment": representation.get("assessment", {}),
        }

# ============================================================
# PUBLIC VALIDATION API
# ============================================================

def validate_assessment_payload(payload: dict[str, Any]) -> dict[str, Any]:
    serializer = CombinedAssessmentSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    validated = serializer.build_feature_builder_payload()
    return Normalizer.json_safe(validated)

def validate_profile_payload(profile_data: dict[str, Any]) -> dict[str, Any]:
    serializer = ProfileSerializer(data=profile_data)
    serializer.is_valid(raise_exception=True)
    return Normalizer.json_safe(serializer.validated_data)

def validate_assessment_only(assessment_data: dict[str, Any]) -> dict[str, Any]:
    serializer = AssessmentSerializer(data=assessment_data)
    serializer.is_valid(raise_exception=True)
    return Normalizer.json_safe(serializer.validated_data)

# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    "ProfileSerializer",
    "AssessmentSerializer",
    "CombinedAssessmentSerializer",
    "NormalizationHelper",
    "validate_assessment_payload",
    "validate_profile_payload",
    "validate_assessment_only",
]