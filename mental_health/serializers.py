from rest_framework import serializers


class ProfileSerializer(serializers.Serializer):
    """
    User profile / demographic / academic info
    used by multiple models during feature building.
    """

    name = serializers.CharField(required=False, allow_blank=True, default="")
    age = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # academic profile
    course = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_year = serializers.IntegerField(required=False, allow_null=True)
    cgpa = serializers.FloatField(required=False, allow_null=True)

    # optional background fields
    college_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    residence_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    relationship_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # optional lifestyle / identity fields
    physical_activity = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    diet_quality = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_history = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    chronic_illness = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_age(self, value):
        if value is not None and (value < 10 or value > 100):
            raise serializers.ValidationError("Age must be between 10 and 100.")
        return value

    def validate_cgpa(self, value):
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("CGPA must be between 0 and 10.")
        return value


class AssessmentAnswersSerializer(serializers.Serializer):
    """
    Unified assessment answers payload.

    Since different models require different fields,
    we keep this serializer flexible and validate the most important
    shared fields only. The remaining fields can still pass through
    because feature_builder.py will selectively consume them.
    """

    # ---------- Core wellness / stress / burnout ----------
    sleep_hours = serializers.FloatField(required=False, allow_null=True)
    screen_time_hours = serializers.FloatField(required=False, allow_null=True)
    study_hours = serializers.FloatField(required=False, allow_null=True)
    study_hours_per_day = serializers.FloatField(required=False, allow_null=True)

    stress_level = serializers.FloatField(required=False, allow_null=True)
    exam_pressure = serializers.FloatField(required=False, allow_null=True)
    academic_pressure = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    academic_performance = serializers.FloatField(required=False, allow_null=True)

    anxiety_score = serializers.FloatField(required=False, allow_null=True)
    depression_score = serializers.FloatField(required=False, allow_null=True)
    burnout_score = serializers.FloatField(required=False, allow_null=True)

    social_support = serializers.FloatField(required=False, allow_null=True)
    physical_activity = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    financial_stress = serializers.FloatField(required=False, allow_null=True)
    family_expectation = serializers.FloatField(required=False, allow_null=True)

    caffeine_intake = serializers.FloatField(required=False, allow_null=True)
    daily_reflections = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mood_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sentiment_score = serializers.FloatField(required=False, allow_null=True)
    steps_per_day = serializers.IntegerField(required=False, allow_null=True)

    # ---------- Student mental health survey ----------
    depression_level = serializers.FloatField(required=False, allow_null=True)
    anxiety_level = serializers.FloatField(required=False, allow_null=True)
    sleep_quality = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    diet_quality = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    counseling_service_use = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    extracurricular_involvement = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    semester_credit_load = serializers.FloatField(required=False, allow_null=True)
    substance_use = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # ---------- MXMH / music ----------
    primary_streaming_service = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    music_hours_per_day = serializers.FloatField(required=False, allow_null=True)
    hours_per_day = serializers.FloatField(required=False, allow_null=True)

    while_working = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instrumentalist = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    composer = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    exploratory = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    foreign_languages = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    fav_genre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bpm = serializers.FloatField(required=False, allow_null=True)

    freq_classical = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_edm = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_folk = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_gospel = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_hip_hop = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_jazz = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_k_pop = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_latin = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_lofi = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_metal = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_pop = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_rnb = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_rap = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_rock = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    freq_video_game_music = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    insomnia = serializers.FloatField(required=False, allow_null=True)
    ocd = serializers.FloatField(required=False, allow_null=True)
    music_effects = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # ---------- Stress dataset style fields ----------
    recent_stress = serializers.FloatField(required=False, allow_null=True)
    rapid_heartbeat = serializers.FloatField(required=False, allow_null=True)
    anxiety_tension = serializers.FloatField(required=False, allow_null=True)
    sleep_problems = serializers.FloatField(required=False, allow_null=True)
    headaches = serializers.FloatField(required=False, allow_null=True)
    irritability = serializers.FloatField(required=False, allow_null=True)
    concentration_issues = serializers.FloatField(required=False, allow_null=True)
    sadness_low_mood = serializers.FloatField(required=False, allow_null=True)
    illness_health_issues = serializers.FloatField(required=False, allow_null=True)
    loneliness = serializers.FloatField(required=False, allow_null=True)
    academic_workload = serializers.FloatField(required=False, allow_null=True)
    peer_competition = serializers.FloatField(required=False, allow_null=True)
    relationship_stress = serializers.FloatField(required=False, allow_null=True)
    professor_difficulty = serializers.FloatField(required=False, allow_null=True)
    work_environment_stress = serializers.FloatField(required=False, allow_null=True)
    lack_of_relaxation = serializers.FloatField(required=False, allow_null=True)
    home_environment_difficulty = serializers.FloatField(required=False, allow_null=True)
    lack_confidence_performance = serializers.FloatField(required=False, allow_null=True)
    lack_confidence_subjects = serializers.FloatField(required=False, allow_null=True)
    academic_extra_conflict = serializers.FloatField(required=False, allow_null=True)
    class_attendance = serializers.FloatField(required=False, allow_null=True)
    weight_change = serializers.FloatField(required=False, allow_null=True)

    # ---------- Extra flexible input bucket ----------
    # If frontend wants to send extra fields later, put them inside "extra"
    extra = serializers.DictField(required=False, default=dict)

    def validate(self, attrs):
        """
        Cross-field validation.
        At least some meaningful assessment data should exist.
        """

        numeric_signal_fields = [
            "sleep_hours",
            "screen_time_hours",
            "study_hours",
            "study_hours_per_day",
            "stress_level",
            "anxiety_score",
            "depression_score",
            "exam_pressure",
            "burnout_score",
            "music_hours_per_day",
            "hours_per_day",
            "bpm",
        ]

        categorical_signal_fields = [
            "fav_genre",
            "music_effects",
            "sleep_quality",
            "physical_activity",
            "diet_quality",
            "mood_description",
        ]

        has_numeric = any(attrs.get(field) is not None for field in numeric_signal_fields)
        has_categorical = any(attrs.get(field) not in [None, ""] for field in categorical_signal_fields)

        if not has_numeric and not has_categorical:
            raise serializers.ValidationError(
                "At least some assessment answer fields must be provided."
            )

        return attrs


class AssessmentSubmitSerializer(serializers.Serializer):
    """
    Main request serializer for POST /assessment/submit/
    """

    profile = ProfileSerializer(required=True)
    answers = AssessmentAnswersSerializer(required=True)


class AssessmentQuestionsResponseSerializer(serializers.Serializer):
    """
    Optional response serializer if later you want
    structured docs for question API.
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()


class AssessmentSubmitResponseSerializer(serializers.Serializer):
    """
    Optional response serializer for docs / consistency.
    """
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField()