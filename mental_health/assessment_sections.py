# mental_health/assessment_sections.py

from .question_bank import UNIFIED_QUESTION_BANK


ASSESSMENT_SECTIONS = [
    {
        "key": "profile",
        "title": "Profile",
        "description": "Basic academic and demographic details"
    },
    {
        "key": "academics",
        "title": "Academic Pressure",
        "description": "Study routine, workload, performance and exam pressure"
    },
    {
        "key": "mental_health",
        "title": "Stress, Anxiety & Mood",
        "description": "Current emotional state and burnout-related signals"
    },
    {
        "key": "sleep_lifestyle",
        "title": "Sleep & Lifestyle",
        "description": "Sleep, screen time, activity and day-to-day wellness habits"
    },
    {
        "key": "social_environment",
        "title": "Support & Environment",
        "description": "Family, social support, finances and surrounding environment"
    },
    {
        "key": "physical_symptoms",
        "title": "Physical Symptoms",
        "description": "Stress-related physical indicators"
    },
    {
        "key": "music",
        "title": "Music & Coping Habits",
        "description": "Music listening behaviour and its perceived impact"
    },
    {
        "key": "reflection",
        "title": "Reflection",
        "description": "Optional open-ended reflection"
    }
]


def get_questions_by_section(section_key: str):
    return [q for q in UNIFIED_QUESTION_BANK if q["section"] == section_key]


def get_assessment_structure():
    result = []
    for section in ASSESSMENT_SECTIONS:
        section_data = {
            "key": section["key"],
            "title": section["title"],
            "description": section["description"],
            "questions": get_questions_by_section(section["key"])
        }
        result.append(section_data)
    return result