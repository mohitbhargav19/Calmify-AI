# mental_health/profile_questions.py

PROFILE_QUESTIONS = [
    {
        "section_id": "basic_profile",
        "section_title": "Basic Profile",
        "description": "Basic personal and academic information used across all assessments.",
        "questions": [
            {
                "key": "name",
                "label": "What is your name?",
                "type": "text",
                "required": False,
                "placeholder": "Enter your name"
            },
            {
                "key": "age",
                "label": "What is your age?",
                "type": "number",
                "required": True,
                "min": 10,
                "max": 100
            },
            {
                "key": "gender",
                "label": "What is your gender?",
                "type": "select",
                "required": True,
                "options": ["Male", "Female", "Other"]
            },
            {
                "key": "course",
                "label": "Which course/stream are you currently studying?",
                "type": "select",
                "required": False,
                "options": [
                    "Computer Science",
                    "Engineering",
                    "Medical",
                    "Business",
                    "Arts",
                    "Others"
                ]
            },
            {
                "key": "academic_year",
                "label": "Which academic year/semester are you currently in?",
                "type": "number",
                "required": False,
                "min": 1,
                "max": 8
            },
            {
                "key": "cgpa",
                "label": "What is your current CGPA / GPA?",
                "type": "number",
                "required": False,
                "min": 0,
                "max": 10,
                "step": 0.01
            },
            {
                "key": "residence_type",
                "label": "Where do you currently live?",
                "type": "select",
                "required": False,
                "options": [
                    "On-Campus",
                    "Off-Campus",
                    "Hostel",
                    "With Family",
                    "Other"
                ]
            },
            {
                "key": "relationship_status",
                "label": "What is your current relationship status?",
                "type": "select",
                "required": False,
                "options": [
                    "Single",
                    "In a Relationship",
                    "Married",
                    "Prefer not to say"
                ]
            },
            {
                "key": "family_history",
                "label": "Do you have a family history of mental health difficulties?",
                "type": "select",
                "required": False,
                "options": ["Yes", "No", "Not Sure"]
            },
            {
                "key": "chronic_illness",
                "label": "Do you have any chronic illness or ongoing health condition?",
                "type": "select",
                "required": False,
                "options": ["Yes", "No"]
            }
        ]
    }
]