from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from .utils import make_json_safe

logger = logging.getLogger(__name__)

PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"

RISK_HIGH = "High"
RISK_MODERATE = "Moderate"
RISK_LOW = "Low"

DEFAULT_CALM_GENRES = ["Lo-fi", "Ambient", "Classical"]
DEFAULT_FOCUS_GENRES = ["Instrumental", "Video Game Music", "Lo-fi"]
DEFAULT_ENERGY_GENRES = ["Pop", "Soft Rock", "Indie"]


class RecommendationEngine:
    """
    Generates personalized recommendations based on user profiles,
    assessment answers, and AI prediction data bundles.
    """

    def __init__(self) -> None:
        logger.info("RecommendationEngine initialized.")

    def _extract_prediction_data(self, prediction_bundle: Dict[str, Any]) -> Dict[str, Any]:
        prediction_bundle = prediction_bundle or {}
        predictions = prediction_bundle.get("predictions", {})
        summary = prediction_bundle.get("combined_summary", {})

        burnout = predictions.get("burnout", {})
        wellness = predictions.get("wellness", {})
        mental = predictions.get("mental_health_status", {})
        student = predictions.get("student_survey", {})
        stress = predictions.get("stress_dataset", {})
        mxmh_case1 = predictions.get("mxmh_case1", {})
        mxmh_case2 = predictions.get("mxmh_case2", {})

        prediction_data = {
            "burnout_score": burnout.get("burnout_score", burnout.get("prediction", 0.0)),
            "burnout_level": burnout.get("prediction_label", "Unknown"),
            "burnout_confidence": burnout.get("confidence"),
            
            "wellness_score": wellness.get("wellness_score", wellness.get("prediction", 0.0)),
            "wellness_level": wellness.get("prediction_label", "Unknown"),
            "wellness_confidence": wellness.get("confidence"),
            
            "mental_health_status": mental.get("prediction_label", "Unknown"),
            "mental_health_confidence": mental.get("confidence"),
            
            "student_stress": student.get("prediction_label", "Unknown"),
            "student_confidence": student.get("confidence"),
            
            "stress_dataset": stress.get("prediction_label", "Unknown"),
            "stress_confidence": stress.get("confidence"),
            
            "recommended_genres": mxmh_case1.get("recommended_genres", []),
            "music_reasoning": mxmh_case1.get("reasoning", []),
            "music_effect": mxmh_case2.get("prediction_label", "Unknown"),
            "music_confidence": mxmh_case2.get("confidence"),
            
            "overall_risk_level": summary.get("overall_risk_level", RISK_MODERATE),
            "overall_confidence": summary.get("overall_confidence"),
        }

        logger.info("Prediction data normalized successfully.")
        return make_json_safe(prediction_data)

    def _extract_user_context(
        self, profile_answers: Dict[str, Any], assessment_answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        profile_answers = profile_answers or {}
        assessment_answers = assessment_answers or {}

        context = {
            "name": profile_answers.get("name", ""),
            "age": profile_answers.get("age"),
            "gender": profile_answers.get("gender"),
            "course": profile_answers.get("course"),
            "academic_year": profile_answers.get("academic_year"),
            "city": profile_answers.get("city"),
            
            "sleep_hours": float(assessment_answers.get("sleep_hours", 0)),
            "study_hours": float(assessment_answers.get("study_hours", 0)),
            "screen_time": float(assessment_answers.get("screen_time", 0)),
            "physical_activity": float(assessment_answers.get("physical_activity", 0)),
            
            "stress_level": float(assessment_answers.get("stress_level", 0)),
            "anxiety_score": float(assessment_answers.get("anxiety_score", 0)),
            "depression_score": float(assessment_answers.get("depression_score", 0)),
            "exam_pressure": float(assessment_answers.get("exam_pressure", 0)),
            "social_support": float(assessment_answers.get("social_support", 0)),
            "financial_stress": float(assessment_answers.get("financial_stress", 0)),
            "family_expectation": float(assessment_answers.get("family_expectation", 0)),
            
            "favorite_genre": assessment_answers.get("favorite_genre"),
            "hours_per_day_music": float(assessment_answers.get("hours_per_day_music", 0)),
            "music_effect": assessment_answers.get("music_effect"),
            "while_working": bool(assessment_answers.get("while_working", False)),
            "exploratory": bool(assessment_answers.get("exploratory", False)),
            "insomnia": bool(assessment_answers.get("insomnia", False)),
            "ocd": bool(assessment_answers.get("ocd", False)),
            
            "journal_text": assessment_answers.get("journal_text", ""),
        }

        logger.info("User context extracted successfully.")
        return make_json_safe(context)

    def _build_top_recommendations(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []

        overall_risk = prediction_data.get("overall_risk_level", RISK_MODERATE)
        burnout = prediction_data.get("burnout_level", "")
        wellness = prediction_data.get("wellness_level", "")
        mental = prediction_data.get("mental_health_status", "")

        sleep = user_context.get("sleep_hours", 0)
        stress = user_context.get("stress_level", 0)
        physical_activity = user_context.get("physical_activity", 0)

        if overall_risk == RISK_HIGH:
            recommendations.append({
                "title": "Immediate Mental Health Support",
                "priority": PRIORITY_HIGH,
                "description": "Your assessment indicates a high overall mental health risk. Consider speaking with a qualified mental health professional.",
            })

        if burnout.lower().startswith("high"):
            recommendations.append({
                "title": "Reduce Burnout",
                "priority": PRIORITY_HIGH,
                "description": "Reduce continuous study sessions, introduce scheduled breaks and improve recovery time.",
            })
        elif burnout.lower().startswith("moderate"):
            recommendations.append({
                "title": "Prevent Burnout",
                "priority": PRIORITY_MEDIUM,
                "description": "Maintain a healthy balance between academic work and personal recovery.",
            })

        if "poor" in wellness.lower():
            recommendations.append({
                "title": "Improve Daily Wellness",
                "priority": PRIORITY_HIGH,
                "description": "Focus on sleep, hydration, nutrition and consistent physical activity.",
            })

        if mental.lower() == "at risk":
            recommendations.append({
                "title": "Mental Health Monitoring",
                "priority": PRIORITY_HIGH,
                "description": "Monitor your emotional wellbeing and seek support if symptoms continue.",
            })

        if sleep < 6:
            recommendations.append({
                "title": "Increase Sleep Duration",
                "priority": PRIORITY_MEDIUM,
                "description": "Aim for at least 7–8 hours of sleep every night.",
            })

        if stress >= 7:
            recommendations.append({
                "title": "Stress Management",
                "priority": PRIORITY_HIGH,
                "description": "Practice relaxation exercises and avoid long continuous work sessions.",
            })

        if physical_activity < 2:
            recommendations.append({
                "title": "Increase Physical Activity",
                "priority": PRIORITY_MEDIUM,
                "description": "Include light exercise or walking for 20–30 minutes daily.",
            })

        if not recommendations:
            recommendations.append({
                "title": "Maintain Healthy Habits",
                "priority": PRIORITY_LOW,
                "description": "Continue your current healthy lifestyle and repeat the assessment periodically.",
            })

        return make_json_safe(recommendations)

    def _build_alerts(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []

        overall_risk = prediction_data.get("overall_risk_level", RISK_MODERATE)
        burnout = prediction_data.get("burnout_level", "")
        mental_status = prediction_data.get("mental_health_status", "")

        stress_level = float(user_context.get("stress_level", 0))
        anxiety = float(user_context.get("anxiety_score", 0))
        depression = float(user_context.get("depression_score", 0))
        sleep = float(user_context.get("sleep_hours", 0))

        if overall_risk == RISK_HIGH:
            alerts.append({
                "priority": PRIORITY_HIGH,
                "title": "High Overall Risk",
                "message": "Overall assessment indicates elevated mental health risk.",
            })

        if burnout.lower().startswith("high"):
            alerts.append({
                "priority": PRIORITY_HIGH,
                "title": "Severe Burnout",
                "message": "Burnout level is critically high. Recovery is recommended.",
            })

        if mental_status.lower() == "at risk":
            alerts.append({
                "priority": PRIORITY_HIGH,
                "title": "Mental Health Concern",
                "message": "Mental health assessment indicates possible concern.",
            })

        if stress_level >= 9:
            alerts.append({
                "priority": PRIORITY_HIGH,
                "title": "Extreme Stress",
                "message": "Stress level is extremely high.",
            })

        if anxiety >= 9:
            alerts.append({
                "priority": PRIORITY_HIGH,
                "title": "Severe Anxiety",
                "message": "Very high anxiety score detected.",
            })

        if depression >= 9:
            alerts.append({
                "priority": PRIORITY_HIGH,
                "title": "Severe Depression Indicators",
                "message": "Depression score requires immediate attention.",
            })

        if sleep <= 4:
            alerts.append({
                "priority": PRIORITY_MEDIUM,
                "title": "Critical Sleep Deficit",
                "message": "Very low sleep duration detected.",
            })

        return make_json_safe(alerts)

    def _build_self_care_plan(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        plan: List[Dict[str, Any]] = []

        burnout = prediction_data.get("burnout_level", "")
        wellness = prediction_data.get("wellness_level", "")
        overall_risk = prediction_data.get("overall_risk_level", RISK_MODERATE)

        sleep = float(user_context.get("sleep_hours", 0))
        physical_activity = float(user_context.get("physical_activity", 0))
        screen_time = float(user_context.get("screen_time", 0))
        stress = float(user_context.get("stress_level", 0))

        if burnout.lower().startswith("high"):
            plan.append({
                "title": "Daily Recovery Time",
                "priority": PRIORITY_HIGH,
                "action": "Schedule at least one uninterrupted recovery period every day.",
            })
        elif burnout.lower().startswith("moderate"):
            plan.append({
                "title": "Balanced Study Routine",
                "priority": PRIORITY_MEDIUM,
                "action": "Follow a structured study schedule with regular breaks.",
            })

        if "poor" in wellness.lower():
            plan.append({
                "title": "Healthy Lifestyle",
                "priority": PRIORITY_HIGH,
                "action": "Focus on hydration, nutrition and consistent daily routine.",
            })

        if sleep < 7:
            plan.append({
                "title": "Improve Sleep",
                "priority": PRIORITY_MEDIUM,
                "action": "Maintain a consistent sleep schedule aiming for 7–8 hours.",
            })

        if physical_activity < 2:
            plan.append({
                "title": "Exercise",
                "priority": PRIORITY_MEDIUM,
                "action": "Walk or perform light exercise for at least 20–30 minutes daily.",
            })

        if screen_time > 8:
            plan.append({
                "title": "Reduce Screen Time",
                "priority": PRIORITY_LOW,
                "action": "Limit unnecessary screen usage, especially before bedtime.",
            })

        if stress >= 7:
            plan.append({
                "title": "Stress Recovery",
                "priority": PRIORITY_HIGH,
                "action": "Practice mindfulness, breathing exercises or meditation daily.",
            })

        if overall_risk == RISK_HIGH:
            plan.append({
                "title": "Professional Support",
                "priority": PRIORITY_HIGH,
                "action": "Consider consulting a mental health professional if symptoms persist.",
            })

        if not plan:
            plan.append({
                "title": "Maintain Current Routine",
                "priority": PRIORITY_LOW,
                "action": "Continue your healthy habits and reassess periodically.",
            })

        return make_json_safe(plan)

    def _build_coping_tips(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        tips: List[Dict[str, Any]] = []

        stress = float(user_context.get("stress_level", 0))
        anxiety = float(user_context.get("anxiety_score", 0))
        depression = float(user_context.get("depression_score", 0))
        sleep = float(user_context.get("sleep_hours", 0))
        screen_time = float(user_context.get("screen_time", 0))
        study_hours = float(user_context.get("study_hours", 0))
        social_support = float(user_context.get("social_support", 0))

        if stress >= 7:
            tips.append({
                "category": "Stress",
                "tip": "Practice deep breathing or meditation for 5–10 minutes daily.",
            })

        if anxiety >= 7:
            tips.append({
                "category": "Anxiety",
                "tip": "Use grounding techniques such as the 5-4-3-2-1 method during anxious moments.",
            })

        if depression >= 7:
            tips.append({
                "category": "Mood",
                "tip": "Stay connected with trusted friends or family and maintain a daily routine.",
            })

        if sleep < 6:
            tips.append({
                "category": "Sleep",
                "tip": "Avoid screens at least one hour before bedtime and maintain a fixed sleep schedule.",
            })

        if screen_time >= 8:
            tips.append({
                "category": "Digital Wellbeing",
                "tip": "Take a 5-minute screen break every hour and reduce unnecessary device usage.",
            })

        if study_hours >= 8:
            tips.append({
                "category": "Study",
                "tip": "Use techniques such as Pomodoro (25–30 minute focused sessions with short breaks).",
            })

        if social_support <= 3:
            tips.append({
                "category": "Support",
                "tip": "Reach out to someone you trust or participate in supportive communities.",
            })

        if not tips:
            tips.append({
                "category": "General",
                "tip": "Continue maintaining your healthy routine and monitor your wellbeing regularly.",
            })

        return make_json_safe(tips)

    def _build_music_recommendations(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []

        burnout = str(prediction_data.get("burnout_level", "")).lower()
        wellness = str(prediction_data.get("wellness_level", "")).lower()
        overall_risk = str(prediction_data.get("overall_risk_level", "")).lower()
        music_effect = str(prediction_data.get("music_effect", "")).lower()
        favourite = str(user_context.get("favorite_genre", "")).strip()

        sleep = float(user_context.get("sleep_hours", 0))
        stress = float(user_context.get("stress_level", 0))

        if "worsen" in music_effect:
            recommendations.append({
                "priority": PRIORITY_HIGH,
                "context": "Music Usage",
                "genres": ["Ambient", "Nature Sounds", "Soft Instrumental"],
                "reason": "Current listening pattern appears to negatively affect mood.",
            })
            return make_json_safe(recommendations)

        if "high" in burnout:
            recommendations.append({
                "priority": PRIORITY_HIGH,
                "context": "Burnout Recovery",
                "genres": DEFAULT_CALM_GENRES,
                "reason": "Slow relaxing music may help reduce mental fatigue.",
            })
        elif "moderate" in burnout:
            recommendations.append({
                "priority": PRIORITY_MEDIUM,
                "context": "Focus",
                "genres": DEFAULT_FOCUS_GENRES,
                "reason": "Instrumental music may improve concentration.",
            })

        if "poor" in wellness:
            recommendations.append({
                "priority": PRIORITY_HIGH,
                "context": "Mood",
                "genres": DEFAULT_ENERGY_GENRES,
                "reason": "Positive emotionally balanced music may improve wellbeing.",
            })

        if stress >= 7:
            recommendations.append({
                "priority": PRIORITY_HIGH,
                "context": "Stress Reduction",
                "genres": ["Meditation", "Relaxation", "Nature Sounds"],
                "reason": "Calming music may reduce physiological stress.",
            })

        if sleep < 6:
            recommendations.append({
                "priority": PRIORITY_MEDIUM,
                "context": "Sleep",
                "genres": ["Sleep Music", "Ambient", "Piano"],
                "reason": "Slow instrumental music before bedtime may improve sleep.",
            })

        if overall_risk == "high":
            recommendations.append({
                "priority": PRIORITY_HIGH,
                "context": "Emotional Regulation",
                "genres": ["Healing Frequencies", "Mindfulness Music"],
                "reason": "Music should support emotional regulation together with professional guidance.",
            })

        if favourite:
            recommendations.append({
                "priority": PRIORITY_LOW,
                "context": "Personal Preference",
                "genres": [favourite],
                "reason": "Including familiar music can improve engagement.",
            })

        if not recommendations:
            recommendations.append({
                "priority": PRIORITY_LOW,
                "context": "General",
                "genres": DEFAULT_CALM_GENRES,
                "reason": "Balanced music suitable for relaxation and studying.",
            })

        return make_json_safe(recommendations)

    def _build_positive_signals(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        positive_signals: List[Dict[str, Any]] = []

        burnout = str(prediction_data.get("burnout_level", "")).lower()
        wellness = str(prediction_data.get("wellness_level", "")).lower()
        overall_risk = str(prediction_data.get("overall_risk_level", "")).lower()

        sleep = float(user_context.get("sleep_hours", 0))
        physical_activity = float(user_context.get("physical_activity", 0))
        social_support = float(user_context.get("social_support", 0))
        stress = float(user_context.get("stress_level", 0))

        if overall_risk == RISK_LOW:
            positive_signals.append({
                "title": "Low Overall Risk",
                "description": "Overall assessment indicates a healthy mental wellbeing profile.",
            })

        if "low" in burnout:
            positive_signals.append({
                "title": "Low Burnout",
                "description": "Burnout risk appears to be well managed.",
            })

        if "good" in wellness:
            positive_signals.append({
                "title": "Good Wellness",
                "description": "Overall wellness indicators are positive.",
            })

        if sleep >= 7:
            positive_signals.append({
                "title": "Healthy Sleep",
                "description": "Your sleep duration supports good recovery.",
            })

        if physical_activity >= 3:
            positive_signals.append({
                "title": "Physically Active",
                "description": "Regular physical activity supports mental health.",
            })

        if social_support >= 6:
            positive_signals.append({
                "title": "Strong Support System",
                "description": "You appear to have good social support.",
            })

        if stress <= 3:
            positive_signals.append({
                "title": "Well Managed Stress",
                "description": "Current stress level is within a healthy range.",
            })

        return make_json_safe(positive_signals)

    def _build_red_flags(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        red_flags: List[Dict[str, Any]] = []

        burnout = str(prediction_data.get("burnout_level", "")).lower()
        wellness = str(prediction_data.get("wellness_level", "")).lower()
        overall_risk = str(prediction_data.get("overall_risk_level", "")).lower()
        mental_status = str(prediction_data.get("mental_health_status", "")).lower()

        stress = float(user_context.get("stress_level", 0))
        anxiety = float(user_context.get("anxiety_score", 0))
        depression = float(user_context.get("depression_score", 0))
        sleep = float(user_context.get("sleep_hours", 0))
        screen_time = float(user_context.get("screen_time", 0))

        if overall_risk == RISK_HIGH:
            red_flags.append({
                "title": "High Overall Risk",
                "severity": PRIORITY_HIGH,
                "description": "Overall assessment indicates elevated mental health risk.",
            })

        if mental_status == "at risk":
            red_flags.append({
                "title": "Mental Health Concern",
                "severity": PRIORITY_HIGH,
                "description": "Mental health prediction indicates possible concern.",
            })

        if burnout.startswith("high"):
            red_flags.append({
                "title": "High Burnout",
                "severity": PRIORITY_HIGH,
                "description": "Burnout level requires immediate recovery strategies.",
            })

        if "poor" in wellness:
            red_flags.append({
                "title": "Poor Wellness",
                "severity": PRIORITY_MEDIUM,
                "description": "Overall wellness indicators are below healthy levels.",
            })

        if stress >= 8:
            red_flags.append({
                "title": "Extreme Stress",
                "severity": PRIORITY_HIGH,
                "description": "Stress score is critically high.",
            })

        if anxiety >= 8:
            red_flags.append({
                "title": "High Anxiety",
                "severity": PRIORITY_HIGH,
                "description": "Anxiety level appears significantly elevated.",
            })

        if depression >= 8:
            red_flags.append({
                "title": "High Depression Score",
                "severity": PRIORITY_HIGH,
                "description": "Depression indicators require attention.",
            })

        if sleep <= 5:
            red_flags.append({
                "title": "Insufficient Sleep",
                "severity": PRIORITY_MEDIUM,
                "description": "Sleep duration is below recommended levels.",
            })

        if screen_time >= 10:
            red_flags.append({
                "title": "Excessive Screen Time",
                "severity": PRIORITY_LOW,
                "description": "High daily screen exposure may affect wellbeing.",
            })

        return make_json_safe(red_flags)

    def _build_follow_up_actions(
        self, prediction_data: Dict[str, Any], user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        burnout = str(prediction_data.get("burnout_level", "")).lower()
        overall_risk = str(prediction_data.get("overall_risk_level", "")).lower()
        mental_status = str(prediction_data.get("mental_health_status", "")).lower()

        stress = float(user_context.get("stress_level", 0))
        anxiety = float(user_context.get("anxiety_score", 0))
        depression = float(user_context.get("depression_score", 0))

        if overall_risk == RISK_HIGH:
            actions.append({
                "priority": PRIORITY_HIGH,
                "timeline": "Immediately",
                "action": "Consult a licensed mental health professional.",
            })

        if mental_status == "at risk":
            actions.append({
                "priority": PRIORITY_HIGH,
                "timeline": "Within 1 week",
                "action": "Schedule a counselling session with a mental health expert.",
            })

        if burnout.startswith("high"):
            actions.append({
                "priority": PRIORITY_HIGH,
                "timeline": "This week",
                "action": "Reduce workload and review your academic or work schedule.",
            })
        elif burnout.startswith("moderate"):
            actions.append({
                "priority": PRIORITY_MEDIUM,
                "timeline": "Within 2 weeks",
                "action": "Monitor burnout symptoms and reassess after lifestyle improvements.",
            })

        if stress >= 8:
            actions.append({
                "priority": PRIORITY_HIGH,
                "timeline": "Daily",
                "action": "Practice stress-management techniques and monitor stress levels.",
            })

        if anxiety >= 8:
            actions.append({
                "priority": PRIORITY_MEDIUM,
                "timeline": "Daily",
                "action": "Include relaxation exercises and anxiety coping strategies in your routine.",
            })

        if depression >= 8:
            actions.append({
                "priority": PRIORITY_HIGH,
                "timeline": "Immediately",
                "action": "Seek professional mental health evaluation if symptoms persist.",
            })

        if not actions:
            actions.append({
                "priority": PRIORITY_LOW,
                "timeline": "Next Month",
                "action": "Repeat the assessment periodically to monitor your wellbeing.",
            })

        return make_json_safe(actions)

    def generate(
        self,
        assessment_answers: Dict[str, Any],
        profile_answers: Optional[Dict[str, Any]] = None,
        prediction_bundle: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        profile_answers = profile_answers or {}
        assessment_answers = assessment_answers or {}
        prediction_bundle = prediction_bundle or {}

        logger.info("Generating recommendation bundle.")

        prediction_data = self._extract_prediction_data(prediction_bundle)
        user_context = self._extract_user_context(
            assessment_answers=assessment_answers,
            profile_answers=profile_answers,
        )

        result = {
            "top_recommendations": self._build_top_recommendations(prediction_data, user_context),
            "alerts": self._build_alerts(prediction_data, user_context),
            "self_care_plan": self._build_self_care_plan(prediction_data, user_context),
            "coping_tips": self._build_coping_tips(prediction_data, user_context),
            "music_recommendations": self._build_music_recommendations(prediction_data, user_context),
            "positive_signals": self._build_positive_signals(prediction_data, user_context),
            "red_flags": self._build_red_flags(prediction_data, user_context),
            "follow_up_actions": self._build_follow_up_actions(prediction_data, user_context),
        }

        logger.info("Recommendation bundle generated successfully.")
        return make_json_safe(result)


recommendation_engine = RecommendationEngine()


def generate_recommendations(
    assessment_answers: Dict[str, Any],
    profile_answers: Optional[Dict[str, Any]] = None,
    prediction_bundle: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Public recommendation API used by ml_engine.py.
    """
    return recommendation_engine.generate(
        assessment_answers=assessment_answers or {},
        profile_answers=profile_answers or {},
        prediction_bundle=prediction_bundle or {},
    )