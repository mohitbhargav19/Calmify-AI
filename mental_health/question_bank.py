# mental_health/question_bank.py

from .profile_questions import PROFILE_QUESTIONS


QUESTION_BANK = [
    # =========================================================
    # SECTION 1 — DAILY WELLNESS / LIFESTYLE
    # Used in: wellness + burnout + overall risk
    # =========================================================
    {
        "section_id": "daily_wellness",
        "section_title": "Daily Wellness & Lifestyle",
        "description": "Questions about your sleep, study routine, physical activity and day-to-day wellbeing.",
        "questions": [
            {
                "key": "sleep_hours",
                "label": "On average, how many hours do you sleep per day?",
                "type": "number",
                "required": True,
                "min": 0,
                "max": 24,
                "step": 0.1
            },
            {
                "key": "screen_time_hours",
                "label": "How many hours of screen time do you usually have in a day?",
                "type": "number",
                "required": True,
                "min": 0,
                "max": 24,
                "step": 0.1
            },
            {
                "key": "study_hours",
                "label": "How many hours do you usually study in a day?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 24,
                "step": 0.1
            },
            {
                "key": "study_hours_per_day",
                "label": "How many hours per day do you spend on academic work / study?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 24,
                "step": 0.1
            },
            {
                "key": "physical_activity",
                "label": "How would you describe your physical activity level?",
                "type": "select",
                "required": True,
                "options": [
                    "No",
                    "Yes",
                    "Low",
                    "Moderate",
                    "High"
                ]
            },
            {
                "key": "steps_per_day",
                "label": "Approximately how many steps do you walk in a day?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 50000
            },
            {
                "key": "caffeine_intake",
                "label": "How many caffeinated drinks (tea/coffee/energy drinks) do you consume daily?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 20
            },
            {
                "key": "diet_quality",
                "label": "How would you rate your diet quality?",
                "type": "select",
                "required": False,
                "options": ["Poor", "Average", "Good"]
            },
            {
                "key": "sleep_quality",
                "label": "How would you rate your sleep quality?",
                "type": "select",
                "required": False,
                "options": ["Poor", "Average", "Good"]
            }
        ]
    },

    # =========================================================
    # SECTION 2 — STRESS / BURNOUT / ACADEMIC PRESSURE
    # Used in: burnout + wellness + student survey + stress models
    # =========================================================
    {
        "section_id": "stress_burnout",
        "section_title": "Stress, Burnout & Academic Pressure",
        "description": "Questions about stress, academic pressure, workload and burnout symptoms.",
        "questions": [
            {
                "key": "stress_level",
                "label": "How stressed do you currently feel overall?",
                "type": "slider",
                "required": True,
                "min": 0,
                "max": 10
            },
            {
                "key": "exam_pressure",
                "label": "How much exam pressure do you currently feel?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            },
            {
                "key": "academic_pressure",
                "label": "How would you describe your academic pressure?",
                "type": "select",
                "required": False,
                "options": ["Low", "Medium", "High"]
            },
            {
                "key": "academic_performance",
                "label": "How would you rate your academic performance confidence?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            },
            {
                "key": "financial_stress",
                "label": "How much financial stress do you currently feel?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            },
            {
                "key": "family_expectation",
                "label": "How much pressure do family expectations place on you?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            },
            {
                "key": "social_support",
                "label": "How supported do you feel by friends / family / peers?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            }
        ]
    },

    # =========================================================
    # SECTION 3 — EMOTIONAL / MENTAL HEALTH
    # Used in: mental_health_status + burnout + survey + music support
    # =========================================================
    {
        "section_id": "mental_health_core",
        "section_title": "Mental Health & Emotional State",
        "description": "Questions about anxiety, mood, depression, emotional wellbeing and self-reflection.",
        "questions": [
            {
                "key": "anxiety_score",
                "label": "How intense has your anxiety been recently?",
                "type": "slider",
                "required": True,
                "min": 0,
                "max": 10
            },
            {
                "key": "depression_score",
                "label": "How low / depressed have you been feeling recently?",
                "type": "slider",
                "required": True,
                "min": 0,
                "max": 10
            },
            {
                "key": "burnout_score",
                "label": "How emotionally exhausted or burnt out do you currently feel?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            },
            {
                "key": "daily_reflections",
                "label": "Write a few lines about how you’ve been feeling lately.",
                "type": "textarea",
                "required": False,
                "placeholder": "Describe your thoughts, mood, stress, or anything affecting you..."
            },
            {
                "key": "mood_description",
                "label": "How would you describe your mood today in one word or short phrase?",
                "type": "text",
                "required": False,
                "placeholder": "e.g. calm, tired, overwhelmed, happy"
            },
            {
                "key": "sentiment_score",
                "label": "If you already have a sentiment score from text analysis, enter it here (optional).",
                "type": "number",
                "required": False,
                "min": -1,
                "max": 1,
                "step": 0.0001
            }
        ]
    },

    # =========================================================
    # SECTION 4 — STUDENT MENTAL HEALTH SURVEY FACTORS
    # Used in: students_mental_health_survey model
    # =========================================================
    {
        "section_id": "student_context",
        "section_title": "Student Environment & Academic Context",
        "description": "Questions about social support, habits, campus life, and academic environment.",
        "questions": [
            {
                "key": "counseling_service_use",
                "label": "How often do you use counseling / mental health support services?",
                "type": "select",
                "required": False,
                "options": ["Never", "Occasionally", "Frequently"]
            },
            {
                "key": "extracurricular_involvement",
                "label": "How involved are you in extracurricular activities?",
                "type": "select",
                "required": False,
                "options": ["Low", "Moderate", "High"]
            },
            {
                "key": "semester_credit_load",
                "label": "How many academic credits / subjects are you handling this term?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 50
            },
            {
                "key": "substance_use",
                "label": "How often do you use substances such as smoking / alcohol / similar coping behaviors?",
                "type": "select",
                "required": False,
                "options": ["Never", "Occasionally", "Frequently"]
            }
        ]
    },

    # =========================================================
    # SECTION 5 — MUSIC LISTENING HABITS (MXMH)
    # Used in: mxmh case 1 + case 2
    # =========================================================
    {
        "section_id": "music_habits",
        "section_title": "Music Listening Habits",
        "description": "Questions about your music listening patterns, preferences and usage habits.",
        "questions": [
            {
                "key": "primary_streaming_service",
                "label": "Which streaming service do you use the most?",
                "type": "select",
                "required": False,
                "options": [
                    "Spotify",
                    "YouTube Music",
                    "Apple Music",
                    "Pandora",
                    "Other streaming service",
                    "I don’t use one regularly"
                ]
            },
            {
                "key": "hours_per_day",
                "label": "How many hours per day do you listen to music?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 24,
                "step": 0.1
            },
            {
                "key": "music_hours_per_day",
                "label": "Music listening hours per day (optional duplicate support field).",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 24,
                "step": 0.1
            },
            {
                "key": "while_working",
                "label": "Do you usually listen to music while studying / working?",
                "type": "select",
                "required": False,
                "options": ["Yes", "No"]
            },
            {
                "key": "instrumentalist",
                "label": "Are you an instrumentalist / do you play an instrument?",
                "type": "select",
                "required": False,
                "options": ["Yes", "No"]
            },
            {
                "key": "composer",
                "label": "Do you compose / create music?",
                "type": "select",
                "required": False,
                "options": ["Yes", "No"]
            },
            {
                "key": "exploratory",
                "label": "Do you like exploring new music / artists / genres?",
                "type": "select",
                "required": False,
                "options": ["Yes", "No"]
            },
            {
                "key": "foreign_languages",
                "label": "Do you listen to songs in foreign languages?",
                "type": "select",
                "required": False,
                "options": ["Yes", "No"]
            },
            {
                "key": "fav_genre",
                "label": "What is your favourite music genre?",
                "type": "select",
                "required": False,
                "options": [
                    "Classical",
                    "Country",
                    "EDM",
                    "Folk",
                    "Gospel",
                    "Hip hop",
                    "Jazz",
                    "K pop",
                    "Latin",
                    "Lofi",
                    "Metal",
                    "Pop",
                    "R&B",
                    "Rap",
                    "Rock",
                    "Video game music"
                ]
            },
            {
                "key": "bpm",
                "label": "If you know it, what is the approximate BPM of the music you usually listen to?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 300
            }
        ]
    },

    # =========================================================
    # SECTION 6 — GENRE FREQUENCY MATRIX
    # Used in: mxmh case 1 + case 2
    # =========================================================
    {
        "section_id": "music_frequency_matrix",
        "section_title": "How Frequently Do You Listen to These Genres?",
        "description": "Tell us how often you listen to different genres.",
        "questions": [
            {
                "key": "freq_classical",
                "label": "Classical",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_country",
                "label": "Country",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_edm",
                "label": "EDM",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_folk",
                "label": "Folk",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_gospel",
                "label": "Gospel",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_hip_hop",
                "label": "Hip hop",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_jazz",
                "label": "Jazz",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_k_pop",
                "label": "K-pop",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_latin",
                "label": "Latin",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_lofi",
                "label": "Lofi",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_metal",
                "label": "Metal",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_pop",
                "label": "Pop",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_rnb",
                "label": "R&B",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_rap",
                "label": "Rap",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_rock",
                "label": "Rock",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            },
            {
                "key": "freq_video_game_music",
                "label": "Video Game Music",
                "type": "select",
                "required": False,
                "options": ["Never", "Rarely", "Sometimes", "Very frequently"]
            }
        ]
    },

    # =========================================================
    # SECTION 7 — MUSIC EFFECTS / MUSIC-MENTAL HEALTH
    # Used in: mxmh case 2 + recommendation engine
    # =========================================================
    {
        "section_id": "music_effects_section",
        "section_title": "Music & Mental Health Effects",
        "description": "Tell us how music seems to affect your mental state.",
        "questions": [
            {
                "key": "insomnia",
                "label": "How severe are your sleep / insomnia issues currently?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            },
            {
                "key": "ocd",
                "label": "How intense are repetitive / obsessive thoughts or compulsive tendencies currently?",
                "type": "slider",
                "required": False,
                "min": 0,
                "max": 10
            },
            {
                "key": "music_effects",
                "label": "Overall, how does music affect your mental state?",
                "type": "select",
                "required": False,
                "options": ["Improve", "No effect", "Worsen"]
            }
        ]
    },

    # =========================================================
    # SECTION 8 — STRESS DATASET STYLE DETAILED SYMPTOMS
    # Used in: stress_dataset model
    # =========================================================
    {
        "section_id": "detailed_stress_symptoms",
        "section_title": "Detailed Stress Symptoms & Stressors",
        "description": "Questions about physical, emotional, academic and environmental stress indicators.",
        "questions": [
            {
                "key": "recent_stress",
                "label": "Have you recently experienced stress in your life?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "rapid_heartbeat",
                "label": "Have you noticed rapid heartbeat or palpitations?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "anxiety_tension",
                "label": "Have you been dealing with anxiety or tension recently?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "sleep_problems",
                "label": "Do you face sleep problems or difficulty falling asleep?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "headaches",
                "label": "Have you been getting headaches more often than usual?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "irritability",
                "label": "Do you get irritated easily?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "concentration_issues",
                "label": "Do you have trouble concentrating on academic tasks?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "sadness_low_mood",
                "label": "Have you been feeling sadness or low mood?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "illness_health_issues",
                "label": "Have you been experiencing illness or health issues?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "loneliness",
                "label": "Do you often feel lonely or isolated?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "academic_workload",
                "label": "Do you feel overwhelmed by your academic workload?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "peer_competition",
                "label": "Does competition with peers affect you negatively?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "relationship_stress",
                "label": "Do your relationships often cause stress?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "professor_difficulty",
                "label": "Are you facing difficulties with professors or instructors?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "work_environment_stress",
                "label": "Is your work/study environment unpleasant or stressful?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "lack_of_relaxation",
                "label": "Do you struggle to find time for relaxation and leisure?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "home_environment_difficulty",
                "label": "Is your hostel/home environment causing difficulty?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "lack_confidence_performance",
                "label": "Do you lack confidence in your academic performance?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "lack_confidence_subjects",
                "label": "Do you lack confidence in your choice of academic subjects?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "academic_extra_conflict",
                "label": "Are academic and extracurricular activities conflicting for you?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "class_attendance",
                "label": "How regularly do you attend classes?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            },
            {
                "key": "weight_change",
                "label": "Have you recently gained or lost weight due to stress or routine changes?",
                "type": "slider",
                "required": False,
                "min": 1,
                "max": 5
            }
        ]
    }
]