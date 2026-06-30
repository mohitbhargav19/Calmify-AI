from __future__ import annotations

import json
import joblib
from pathlib import Path
from typing import Any, Dict, List
from .model_feature_mapper import MODEL_FILE_MAP
from .model_feature_mapper import (
    BURNOUT_MODEL,
    WELLNESS_MODEL,
    MENTAL_HEALTH_STATUS_MODEL,
    STUDENT_SURVEY_MODEL,
    MXMH_CASE1_MODEL,
    MXMH_CASE2_MODEL,
    STRESS_DATASET_MODEL,
)

# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"

print("=" * 70)
print("FEATURE BUILDER LOADED")
print("FILE :", Path(__file__).resolve())
print("MODEL DIRECTORY :", MODEL_DIR)
print("=" * 70)

# ==========================================================
# FEATURE COLUMN LOADER
# ==========================================================

def load_feature_columns(filename: str):
    """
    Loads training feature columns from models folder.

    Supports:
        *.json
        *.pkl
    """

    path = MODEL_DIR / filename

    if not path.exists():

        raise FileNotFoundError(
            f"\nFeature file not found:\n{path}"
        )

    if path.suffix.lower() == ".json":

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    return joblib.load(path)

# ==========================================================
# MXMH FEATURE LISTS
# ==========================================================

MXMH_CASE2_COLUMNS = load_feature_columns(
    "mxmh_case2_feature_columns.json"
)

MXMH_EFFECT_COLUMNS = load_feature_columns(
    "mxmh_music_effects_features.pkl"
)

# ==========================================================
# SAFE HELPERS
# ==========================================================

def safe_float(value: Any, default: float = 0.0) -> float:

    try:

        if value in (None, ""):
            return default

        return float(value)

    except Exception:

        return default


def safe_int(value: Any, default: int = 0) -> int:

    try:

        if value in (None, ""):
            return default

        return int(float(value))

    except Exception:

        return default


def safe_str(value: Any, default: str = "") -> str:

    if value is None:

        return default

    value = str(value).strip().lower()

    if value == "":

        return default

    return value

# ==========================================================
# MATHEMATICAL HELPERS
# ==========================================================

def mean(values: List[Any]) -> float:

    cleaned = [
        safe_float(v)
        for v in values
    ]

    if len(cleaned) == 0:

        return 0.0

    return sum(cleaned) / len(cleaned)

# ==========================================================
# GENDER ENCODER
# ==========================================================

def gender_to_numeric(value: Any) -> int:

    value = safe_str(value)

    if value == "male":

        return 1

    if value == "female":

        return 0

    return 2

# ==========================================================
# YES / NO ENCODER
# ==========================================================

def yes_no_to_numeric(value: Any) -> int:

    value = safe_str(value)

    if value in {

        "yes",
        "true",
        "1",
        "y",

    }:

        return 1

    return 0

# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================

def compute_music_engagement(data: Dict[str, Any]) -> float:
    """
    Overall music engagement score.
    Sum of all genre listening frequencies.
    """

    genres = [
        "classical",
        "country",
        "edm",
        "folk",
        "gospel",
        "hip_hop",
        "jazz",
        "k_pop",
        "latin",
        "lofi",
        "metal",
        "pop",
        "rap",
        "rnb",
        "rock",
        "video_game_music",
    ]

    total = 0.0

    for genre in genres:

        total += safe_float(
            data.get(f"freq_{genre}", 0)
        )

    return total


# ----------------------------------------------------------

def compute_calm_score(data: Dict[str, Any]) -> float:
    """
    Calm music preference score.
    """

    return mean([

        safe_float(data.get("freq_classical")),

        safe_float(data.get("freq_lofi")),

        safe_float(data.get("freq_folk")),

        safe_float(data.get("freq_jazz")),

    ])


# ----------------------------------------------------------

def compute_energy_score(data: Dict[str, Any]) -> float:
    """
    High-energy music score.
    """

    return mean([

        safe_float(data.get("freq_edm")),

        safe_float(data.get("freq_rock")),

        safe_float(data.get("freq_metal")),

        safe_float(data.get("freq_rap")),

    ])


# ----------------------------------------------------------

def compute_genre_diversity(data: Dict[str, Any]) -> float:
    """
    Number of genres actively listened to.
    """

    genres = [

        "classical",
        "country",
        "edm",
        "folk",
        "gospel",
        "hip_hop",
        "jazz",
        "k_pop",
        "latin",
        "lofi",
        "metal",
        "pop",
        "rap",
        "rnb",
        "rock",
        "video_game_music",

    ]

    diversity = 0

    for genre in genres:

        if safe_float(
            data.get(f"freq_{genre}", 0)
        ) > 0:

            diversity += 1

    return diversity


# ----------------------------------------------------------

def compute_mental_score(data: Dict[str, Any]) -> float:
    """
    Overall mental health score used in MXMH models.
    """

    return mean([

        safe_float(data.get("anxiety")),

        safe_float(data.get("depression")),

        safe_float(data.get("insomnia")),

        safe_float(data.get("ocd")),

    ])
    
    
    # ==========================================================
# PROFILE FEATURE BUILDER
# ==========================================================

def build_profile_features(profile: dict) -> dict:
    """
    Normalize profile information.

    This function only cleans user profile.
    No model-specific engineered features are generated.
    """

    return {

        # Identity
        "name": safe_str(profile.get("name")),
        "age": safe_int(profile.get("age")),
        "gender": safe_str(profile.get("gender")),

        # Academic
        "college": safe_str(profile.get("college")),
        "course": safe_str(profile.get("course")),
        "branch": safe_str(profile.get("branch")),
        "semester": safe_int(profile.get("semester")),

        "cgpa": safe_float(
            profile.get(
                "cgpa",
                profile.get("gpa", 0),
            )
        ),

        "gpa": safe_float(
            profile.get(
                "gpa",
                profile.get("cgpa", 0),
            )
        ),

        # Location
        "city": safe_str(profile.get("city")),
        "state": safe_str(profile.get("state")),
        "country": safe_str(
            profile.get(
                "country",
                "india",
            )
        ),

        # Lifestyle
        "relationship_status": safe_str(
            profile.get("relationship_status")
        ),

        "residence_type": safe_str(
            profile.get("residence_type")
        ),

        "employment_status": safe_str(
            profile.get(
                "employment_status",
                "student",
            )
        ),
    }
    
# ==========================================================
# BURNOUT FEATURE BUILDER
# ==========================================================

def build_burnout_features(data: dict) -> dict:
    """
    Exact Burnout model features (18)
    """

    study_hours = safe_float(data.get("study_hours"))
    exam_pressure = safe_float(data.get("exam_pressure"))
    academic_performance = safe_float(data.get("academic_performance"))
    anxiety_score = safe_float(data.get("anxiety_score"))
    depression_score = safe_float(data.get("depression_score"))
    stress_level = safe_float(data.get("stress_level"))
    sleep_hours = safe_float(data.get("sleep_hours"))
    physical_activity = safe_float(data.get("physical_activity"))
    social_support = safe_float(data.get("social_support"))
    financial_stress = safe_float(data.get("financial_stress"))
    family_expectation = safe_float(data.get("family_expectation"))

    academic_load = mean([
        study_hours,
        exam_pressure,
    ])

    external_stress = mean([
        financial_stress,
        family_expectation,
    ])

    mental_health_index = mean([
        anxiety_score,
        depression_score,
        stress_level,
    ])

    mental_stress_score = mean([
        anxiety_score,
        depression_score,
        exam_pressure,
    ])

    lifestyle_score = mean([
        sleep_hours,
        physical_activity,
        social_support,
    ])

    sleep_deficit = max(
        0,
        8 - sleep_hours,
    )

    work_life_imbalance = max(
        0,
        study_hours - physical_activity,
    )

    return {

        "academic_load": academic_load,
        "academic_performance": academic_performance,
        "anxiety_score": anxiety_score,
        "depression_score": depression_score,
        "exam_pressure": exam_pressure,
        "external_stress": external_stress,
        "family_expectation": family_expectation,
        "financial_stress": financial_stress,
        "lifestyle_score": lifestyle_score,
        "mental_health_index": mental_health_index,
        "mental_stress_score": mental_stress_score,
        "physical_activity": physical_activity,
        "sleep_deficit": sleep_deficit,
        "sleep_hours": sleep_hours,
        "social_support": social_support,
        "stress_level": stress_level,
        "study_hours_per_day": study_hours,
        "work_life_imbalance": work_life_imbalance,
    }
    
# ==========================================================
# WELLNESS FEATURE BUILDER
# ==========================================================

def build_wellness_features(data: dict) -> dict:
    """
    Build EXACT features required by wellness_model_final.pkl

    Total Features = 16
    """

    age = safe_int(data.get("age"))
    gender = gender_to_numeric(data.get("gender"))

    study_hours = safe_float(data.get("study_hours"))
    screen_time_hours = safe_float(data.get("screen_time_hours"))
    sleep_hours = safe_float(data.get("sleep_hours"))
    stress_level = safe_float(data.get("stress_level"))
    physical_activity = safe_float(data.get("physical_activity"))
    caffeine_intake = safe_float(data.get("caffeine_intake"))
    academic_pressure = safe_float(data.get("academic_pressure"))

    # --------------------------------------------------
    # Engineered Features
    # --------------------------------------------------

    sleep_deficit = max(
        0.0,
        8.0 - sleep_hours,
    )

    sleep_balance_score = mean([
        sleep_hours,
        physical_activity,
    ])

    study_load_score = mean([
        study_hours,
        academic_pressure,
    ])

    stress_pressure_score = mean([
        stress_level,
        academic_pressure,
    ])

    caffeine_burden = mean([
        caffeine_intake,
        stress_level,
    ])

    digital_overload_score = mean([
        screen_time_hours,
        study_hours,
    ])

    lifestyle_support_score = mean([
        physical_activity,
        sleep_hours,
    ])

    return {

        "academic_pressure": academic_pressure,

        "age": age,

        "caffeine_burden": caffeine_burden,

        "caffeine_intake": caffeine_intake,

        "digital_overload_score": digital_overload_score,

        "gender": gender,

        "lifestyle_support_score": lifestyle_support_score,

        "physical_activity": physical_activity,

        "screen_time_hours": screen_time_hours,

        "sleep_balance_score": sleep_balance_score,

        "sleep_deficit": sleep_deficit,

        "sleep_hours": sleep_hours,

        "stress_level": stress_level,

        "stress_pressure_score": stress_pressure_score,

        "study_hours": study_hours,

        "study_load_score": study_load_score,
    }
    
# ==========================================================
# MENTAL HEALTH FEATURE BUILDER
# ==========================================================

def build_mental_health_features(data: dict) -> dict:
    """
    Build EXACT features required by
    mental_health_status_model_v1.pkl

    Total Features = 23
    """

    age = safe_int(data.get("age"))
    gender = gender_to_numeric(data.get("gender"))

    gpa = safe_float(
        data.get(
            "gpa",
            data.get("cgpa"),
        )
    )

    anxiety_score = safe_float(data.get("anxiety_score"))
    depression_score = safe_float(data.get("depression_score"))
    stress_level = safe_float(data.get("stress_level"))
    sleep_hours = safe_float(data.get("sleep_hours"))
    steps_per_day = safe_float(data.get("steps_per_day"))

    mood_description = safe_str(
        data.get("mood_description")
    )

    reflection = safe_str(
        data.get(
            "reflection_text",
            data.get("reflection"),
        )
    )

    # --------------------------------------------------
    # Engineered Features
    # --------------------------------------------------

    sleep_deficit = max(
        0.0,
        8.0 - sleep_hours,
    )

    activity_score = mean([
        steps_per_day,
        sleep_hours,
    ])

    emotional_distress_score = mean([
        anxiety_score,
        depression_score,
        stress_level,
    ])

    overall_mental_risk_score = mean([
        emotional_distress_score,
        sleep_deficit,
    ])

    gpa_risk = max(
        0.0,
        10.0 - gpa,
    )

    # Placeholder NLP features
    mood_score = 0.0
    sentiment_score = 0.0
    mood_description_encoded = 0

    reflection_char_count = len(reflection)

    reflection_word_count = len(
        reflection.split()
    )

    positive_word_count = 0
    negative_word_count = 0
    stress_word_count = 0
    reflection_sentiment_balance = 0.0

    return {

        "activity_score": activity_score,

        "age": age,

        "anxiety_score": anxiety_score,

        "depression_score": depression_score,

        "emotional_distress_score":
            emotional_distress_score,

        "gender": gender,

        "gpa": gpa,

        "gpa_risk": gpa_risk,

        "mood_description":
            mood_description,

        "mood_description_encoded":
            mood_description_encoded,

        "mood_score":
            mood_score,

        "negative_word_count":
            negative_word_count,

        "overall_mental_risk_score":
            overall_mental_risk_score,

        "positive_word_count":
            positive_word_count,

        "reflection_char_count":
            reflection_char_count,

        "reflection_sentiment_balance":
            reflection_sentiment_balance,

        "reflection_word_count":
            reflection_word_count,

        "sentiment_score":
            sentiment_score,

        "sleep_deficit":
            sleep_deficit,

        "sleep_hours":
            sleep_hours,

        "steps_per_day":
            steps_per_day,

        "stress_level":
            stress_level,

        "stress_word_count":
            stress_word_count,
    }
    
# ==========================================================
# STUDENT SURVEY FEATURE BUILDER
# ==========================================================

def build_student_survey_features(data: dict) -> dict:
    """
    Build EXACT features required by stress_features.pkl

    Total Features = 20
    """

    return {

        "academic_performance":
            safe_float(data.get("academic_performance")),

        "anxiety_level":
            safe_float(data.get("anxiety_level")),

        "basic_needs":
            safe_float(data.get("basic_needs")),

        "blood_pressure":
            safe_float(data.get("blood_pressure")),

        "breathing_problem":
            safe_float(data.get("breathing_problem")),

        "bullying":
            safe_float(data.get("bullying")),

        "depression":
            safe_float(data.get("depression")),

        "extracurricular_activities":
            safe_float(data.get("extracurricular_activities")),

        "future_career_concerns":
            safe_float(data.get("future_career_concerns")),

        "headache":
            safe_float(data.get("headache")),

        "living_conditions":
            safe_float(data.get("living_conditions")),

        "mental_health_history":
            safe_float(data.get("mental_health_history")),

        "noise_level":
            safe_float(data.get("noise_level")),

        "peer_pressure":
            safe_float(data.get("peer_pressure")),

        "safety":
            safe_float(data.get("safety")),

        "self_esteem":
            safe_float(data.get("self_esteem")),

        "sleep_quality":
            safe_float(data.get("sleep_quality")),

        "social_support":
            safe_float(data.get("social_support")),

        "study_load":
            safe_float(data.get("study_load")),

        "teacher_student_relationship":
            safe_float(data.get("teacher_student_relationship")),
    }
    
# ==========================================================
# STRESS DATASET FEATURE BUILDER
# ==========================================================

def build_stress_dataset_features(data: dict) -> dict:
    """
    Build EXACT features required by
    stress_dataset_feature_columns.pkl

    Total Features = 20
    """

    return {

        "academic_performance":
            safe_float(data.get("academic_performance")),

        "anxiety_level":
            safe_float(data.get("anxiety_level")),

        "basic_needs":
            safe_float(data.get("basic_needs")),

        "blood_pressure":
            safe_float(data.get("blood_pressure")),

        "breathing_problem":
            safe_float(data.get("breathing_problem")),

        "bullying":
            safe_float(data.get("bullying")),

        "depression":
            safe_float(data.get("depression")),

        "extracurricular_activities":
            safe_float(data.get("extracurricular_activities")),

        "future_career_concerns":
            safe_float(data.get("future_career_concerns")),

        "headache":
            safe_float(data.get("headache")),

        "living_conditions":
            safe_float(data.get("living_conditions")),

        "mental_health_history":
            safe_float(data.get("mental_health_history")),

        "noise_level":
            safe_float(data.get("noise_level")),

        "peer_pressure":
            safe_float(data.get("peer_pressure")),

        "safety":
            safe_float(data.get("safety")),

        "self_esteem":
            safe_float(data.get("self_esteem")),

        "sleep_quality":
            safe_float(data.get("sleep_quality")),

        "social_support":
            safe_float(data.get("social_support")),

        "study_load":
            safe_float(data.get("study_load")),

        "teacher_student_relationship":
            safe_float(data.get("teacher_student_relationship")),
    }
    

# ==========================================================
# SAFE ONE HOT ENCODER
# ==========================================================

def _safe_one_hot(
    feature_dict: dict,
    prefix: str,
    value: str,
) -> None:
    """
    Activate one-hot column ONLY if it exists
    in the saved training feature list.
    """

    if value is None:
        return

    value = safe_str(value).strip().lower()

    for column in feature_dict:

        if not column.startswith(prefix + "_"):
            continue

        suffix = (
            column
            .replace(prefix + "_", "")
            .strip()
            .lower()
        )

        if suffix == value:
            feature_dict[column] = 1.0
            
# ==========================================================
# STREAMING SERVICE ENCODER
# ==========================================================

def encode_streaming_service(
    feature_dict: dict,
    streaming_service,
) -> None:
    """
    Streaming Service One-Hot Encoder
    """

    _safe_one_hot(
        feature_dict,
        "streaming_service",
        streaming_service,
    )
    
# ==========================================================
# FAVOURITE GENRE ENCODER
# ==========================================================

def encode_favourite_genre(
    feature_dict: dict,
    genre,
) -> None:
    """
    Favourite Genre One-Hot Encoder
    """

    _safe_one_hot(
        feature_dict,
        "fav_genre",
        genre,
    )
    
# ==========================================================
# BPM BAND ENCODER
# ==========================================================

def encode_bpm_band(
    feature_dict: dict,
    bpm,
) -> None:

    bpm = safe_float(bpm)

    if bpm < 80:
        band = "low"

    elif bpm < 110:
        band = "medium"

    elif bpm < 140:
        band = "high"

    else:
        band = "very_high"

    _safe_one_hot(
        feature_dict,
        "bpm_band",
        band,
    )
    
# ==========================================================
# LISTENING BAND ENCODER
# ==========================================================

def encode_listening_band(
    feature_dict: dict,
    hours,
) -> None:

    hours = safe_float(hours)

    if hours <= 2:
        band = "low"

    elif hours <= 5:
        band = "moderate"

    else:
        band = "high"

    _safe_one_hot(
        feature_dict,
        "listening_band",
        band,
    )
    
# ==========================================================
# MENTAL HEALTH BAND ENCODER
# ==========================================================

def encode_mental_health_band(
    feature_dict: dict,
    score,
) -> None:

    score = safe_float(score)

    if score < 3:
        band = "low"

    elif score < 7:
        band = "moderate"

    else:
        band = "high"

    _safe_one_hot(
        feature_dict,
        "mental_health_band",
        band,
    )
    
# ==========================================================
# ENCODE LISTENING BAND
# ==========================================================

def encode_listening_band(
    feature_dict: dict,
    hours: float,
) -> None:
    """
    Listening duration bands.
    """

    hours = safe_float(hours)

    if hours <= 2:
        band = "low_listener"

    elif hours <= 5:
        band = "moderate_listener"

    else:
        band = "heavy_listener"

    _safe_one_hot(
        feature_dict,
        "listening_band",
        band,
    )
    
# ==========================================================
# MXMH CASE 2 FEATURE BUILDER
# ==========================================================

def build_mxmh_case2_features(data: dict) -> dict:
    """
    Build EXACT features required by

    mxmh_case2_feature_columns.json

    Returns aligned feature dictionary.
    """

    # --------------------------------------------------
    # Initialize ALL training features
    # --------------------------------------------------

    features = {
        column: 0.0
        for column in MXMH_CASE2_COLUMNS
    }

    # --------------------------------------------------
    # Basic Numeric Features
    # --------------------------------------------------

    numeric_fields = [

        "age",
        "hours_per_day",
        "bpm",
        "anxiety",
        "depression",
        "insomnia",
        "ocd",

    ]

    for field in numeric_fields:

        if field in features:

            features[field] = safe_float(
                data.get(field)
            )

    # --------------------------------------------------
    # Binary Features
    # --------------------------------------------------

    binary_fields = [

        "while_working",
        "instrumentalist",
        "composer",
        "exploratory",
        "foreign_languages",

    ]

    for field in binary_fields:

        if field in features:

            features[field] = yes_no_to_numeric(
                data.get(field)
            )

    # --------------------------------------------------
    # Genre Frequency Features
    # --------------------------------------------------

    genres = [

        "classical",
        "country",
        "edm",
        "folk",
        "gospel",
        "hip_hop",
        "jazz",
        "k_pop",
        "latin",
        "lofi",
        "metal",
        "pop",
        "rap",
        "rnb",
        "rock",
        "video_game_music",

    ]

    for genre in genres:

        column = f"freq_{genre}"

        if column in features:

            features[column] = safe_float(
                data.get(column)
            )

    # --------------------------------------------------
    # Engineered Scores
    # --------------------------------------------------

    if "music_engagement_score" in features:

        features["music_engagement_score"] = (
            compute_music_engagement(data)
        )

    if "genre_diversity_score" in features:

        features["genre_diversity_score"] = (
            compute_genre_diversity(data)
        )

    if "calm_music_score" in features:

        features["calm_music_score"] = (
            compute_calm_score(data)
        )

    if "high_energy_score" in features:

        features["high_energy_score"] = (
            compute_energy_score(data)
        )

    if "mental_health_score" in features:

        features["mental_health_score"] = (
            compute_mental_score(data)
        )

    # --------------------------------------------------
    # One Hot Encoding
    # --------------------------------------------------

    encode_streaming_service(

        features,

        data.get(
            "primary_streaming_service"
        ),

    )

    encode_favourite_genre(

        features,

        data.get(
            "fav_genre"
        ),

    )

    encode_bpm_band(

        features,

        data.get(
            "bpm"
        ),

    )

    encode_listening_band(

        features,

        data.get(
            "hours_per_day"
        ),

    )

    encode_mental_health_band(

        features,

        compute_mental_score(data),

    )

    return features

# ==========================================================
# BUILD ALL MODEL INPUTS
# ==========================================================

def build_all_model_inputs(user_data: dict) -> dict:
    """
    Build raw feature dictionaries for every model.

    Feature alignment is handled later inside
    AIModelService._align_features().
    """

    return {

        BURNOUT_MODEL:
            build_burnout_features(user_data),

        WELLNESS_MODEL:
            build_wellness_features(user_data),

        MENTAL_HEALTH_STATUS_MODEL:
            build_mental_health_features(user_data),

        STUDENT_SURVEY_MODEL:
            build_student_survey_features(user_data),

        STRESS_DATASET_MODEL:
            build_stress_dataset_features(user_data),

        MXMH_CASE2_MODEL:
            build_mxmh_case2_features(user_data),

    }