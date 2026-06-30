"""
model_feature_mapper.py

Central model configuration.

Responsibilities
----------------
• Model names
• File mappings
• Output mappings
• Label mappings
• Rule-based model detection

No model loading.
No prediction logic.
No feature alignment.
"""
def get_model_filename(model_key):

    return MODEL_FILE_MAP.get(model_key)


def get_feature_filename(model_key):

    return FEATURE_COLUMNS_FILE_MAP.get(model_key)


def get_label_encoder_filename(model_key):

    return LABEL_ENCODER_FILE_MAP.get(model_key)
# ==========================================================
# MODEL KEYS
# ==========================================================

BURNOUT_MODEL = "burnout"

WELLNESS_MODEL = "wellness"

MENTAL_HEALTH_STATUS_MODEL = "mental_health_status"

STUDENT_SURVEY_MODEL = "student_survey"

MXMH_CASE1_MODEL = "mxmh_case1"

MXMH_CASE2_MODEL = "mxmh_case2"

STRESS_DATASET_MODEL = "stress_dataset"

# ==========================================================
# MODEL LISTS
# ==========================================================

ALL_MODEL_KEYS = [

    BURNOUT_MODEL,

    WELLNESS_MODEL,

    MENTAL_HEALTH_STATUS_MODEL,

    STUDENT_SURVEY_MODEL,

    MXMH_CASE1_MODEL,

    MXMH_CASE2_MODEL,

    STRESS_DATASET_MODEL,

]

TRAINED_MODEL_KEYS = [

    BURNOUT_MODEL,

    WELLNESS_MODEL,

    MENTAL_HEALTH_STATUS_MODEL,

    STUDENT_SURVEY_MODEL,

    MXMH_CASE2_MODEL,

    STRESS_DATASET_MODEL,

]

RULE_BASED_MODEL_KEYS = [

    MXMH_CASE1_MODEL,

]

# ==========================================================
# MODEL FILES
# ==========================================================

MODEL_FILE_MAP = {

    BURNOUT_MODEL:
        "burnout_model.pkl",

    WELLNESS_MODEL:
        "wellness_model_final.pkl",

    MENTAL_HEALTH_STATUS_MODEL:
        "mental_health_status_model_v1.pkl",

    STUDENT_SURVEY_MODEL:
        "student_survey_stress_model.pkl",

    MXMH_CASE1_MODEL:
        None,

    MXMH_CASE2_MODEL:
        "mxmh_case2_music_effects_xgboost.pkl",

    STRESS_DATASET_MODEL:
        "stress_dataset_best_model.pkl",

}

# ==========================================================
# FEATURE COLUMN FILES
# ==========================================================

FEATURE_COLUMNS_FILE_MAP = {

    BURNOUT_MODEL:
        "burnout_features.pkl",

    WELLNESS_MODEL:
        "wellness_features.pkl",

    MENTAL_HEALTH_STATUS_MODEL:
        "mental_health_status_features_v1.pkl",

    STUDENT_SURVEY_MODEL:
    "student_survey_features.pkl",
    
    MXMH_CASE1_MODEL:
        None,

    MXMH_CASE2_MODEL:
        "mxmh_case2_feature_columns.json",

    STRESS_DATASET_MODEL:
        "stress_dataset_feature_columns.pkl",

}

# ==========================================================
# LABEL ENCODERS
# ==========================================================

LABEL_ENCODER_FILE_MAP = {

    MXMH_CASE2_MODEL:
        "mxmh_music_effects_label_encoder.pkl",

    STRESS_DATASET_MODEL:
        "stress_dataset_label_encoder.pkl",

}

# ==========================================================
# OUTPUT KEYS
# ==========================================================

MODEL_OUTPUT_KEY_MAP = {

    BURNOUT_MODEL:
        BURNOUT_MODEL,

    WELLNESS_MODEL:
        WELLNESS_MODEL,

    MENTAL_HEALTH_STATUS_MODEL:
        MENTAL_HEALTH_STATUS_MODEL,

    STUDENT_SURVEY_MODEL:
        STUDENT_SURVEY_MODEL,

    MXMH_CASE1_MODEL:
        MXMH_CASE1_MODEL,

    MXMH_CASE2_MODEL:
        MXMH_CASE2_MODEL,

    STRESS_DATASET_MODEL:
        STRESS_DATASET_MODEL,

}

# ==========================================================
# TARGET COLUMN NAMES
# ==========================================================

MODEL_TARGET_MAP = {

    BURNOUT_MODEL:
        "burnout_level",

    WELLNESS_MODEL:
        "wellness_level",

    MENTAL_HEALTH_STATUS_MODEL:
        "mental_health_status",

    STUDENT_SURVEY_MODEL:
        "stress_level",

    MXMH_CASE1_MODEL:
        "music_recommendation",

    MXMH_CASE2_MODEL:
        "music_effect",

    STRESS_DATASET_MODEL:
        "stress_category",

}

# ==========================================================
# LABEL MAPS
# ==========================================================

LABEL_MAPS = {

    BURNOUT_MODEL: {

        0: "Low Burnout",
        1: "Moderate Burnout",
        2: "High Burnout",

    },

    WELLNESS_MODEL: {

        0: "Poor Wellness",
        1: "Average Wellness",
        2: "Good Wellness",

    },

    MENTAL_HEALTH_STATUS_MODEL: {

        0: "Healthy",
        1: "At Risk",
        2: "Critical",

    },

    STUDENT_SURVEY_MODEL: {

        0: "Low Stress",
        1: "Moderate Stress",
        2: "High Stress",

    },

}

# ==========================================================
# LABEL MAP LOOKUP
# ==========================================================

def get_label_map(model_key):

    """
    Return manual label mapping.

    Returns {} if unavailable.
    """

    return LABEL_MAPS.get(model_key, {})

# ==========================================================
# RULE BASED CHECK
# ==========================================================

def is_rule_based_model(model_key):

    """
    True if model is rule-based.
    """

    return model_key in RULE_BASED_MODEL_KEYS