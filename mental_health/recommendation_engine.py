# mental_health/recommendation_engine.py

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _safe_lower(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default


def _bool_like(value: Any) -> bool:
    """
    Converts common answer formats into True/False.
    Supports:
    - yes/no
    - true/false
    - 1/0
    """
    if value is None:
        return False

    s = str(value).strip().lower()
    return s in {"yes", "true", "1", "y"}


# ============================================================
# MAIN RECOMMENDATION ENGINE
# ============================================================

class RecommendationEngine:
    """
    Calmify AI Recommendation Engine

    Input:
    - assessment_answers
    - profile_answers
    - prediction_bundle (output from ai_model.predict_user_assessment)

    Output:
    {
        "self_care_plan": [...],
        "coping_tips": [...],
        "music_recommendations": [...],
        "red_flags": [...],
        "positive_signals": [...],
        "follow_up_actions": [...]
    }
    """

    # ========================================================
    # PUBLIC ENTRY
    # ========================================================

    def generate(
        self,
        assessment_answers: Dict[str, Any],
        profile_answers: Optional[Dict[str, Any]] = None,
        prediction_bundle: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        profile_answers = profile_answers or {}
        prediction_bundle = prediction_bundle or {}

        predictions = prediction_bundle.get("predictions", {})
        combined_summary = prediction_bundle.get("combined_summary", {})

        # ----------------------------------------------------
        # Extract useful summary fields
        # ----------------------------------------------------
        burnout_score = combined_summary.get("burnout_score")
        burnout_band = combined_summary.get("burnout_level")
        
        wellness_score = combined_summary.get("wellness_score")
        wellness_band = combined_summary.get("wellness_level")

        mental_health_status = combined_summary.get("mental_health_status")
        stress_type_prediction = combined_summary.get("stress_type_prediction")
        music_effect_prediction = combined_summary.get("music_effect_prediction")
        overall_risk_level = combined_summary.get("overall_risk_level", "Moderate")

        # ----------------------------------------------------
        # Extract assessment signals
        # ----------------------------------------------------
        user_signals = self._extract_user_signals(
            assessment_answers=assessment_answers,
            profile_answers=profile_answers,
            predictions=predictions,
            combined_summary=combined_summary,
        )

        # ----------------------------------------------------
        # Build recommendations
        # ----------------------------------------------------
        self_care_plan = self._build_self_care_plan(
            user_signals=user_signals,
            burnout_band=burnout_band,
            wellness_band=wellness_band,
            overall_risk_level=overall_risk_level,
        )

        coping_tips = self._build_coping_tips(
            user_signals=user_signals,
            stress_type_prediction=stress_type_prediction,
            mental_health_status=mental_health_status,
        )

        music_recommendations = self._build_music_recommendations(
            user_signals=user_signals,
            music_effect_prediction=music_effect_prediction,
            stress_type_prediction=stress_type_prediction,
        )

        red_flags = self._build_red_flags(
            user_signals=user_signals,
            burnout_band=burnout_band,
            mental_health_status=mental_health_status,
            overall_risk_level=overall_risk_level,
        )

        positive_signals = self._build_positive_signals(
            user_signals=user_signals,
            burnout_band=burnout_band,
            wellness_band=wellness_band,
        )

        follow_up_actions = self._build_follow_up_actions(
            user_signals=user_signals,
            burnout_band=burnout_band,
            wellness_band=wellness_band,
            mental_health_status=mental_health_status,
            overall_risk_level=overall_risk_level,
        )

        return {
            "self_care_plan": self_care_plan,
            "coping_tips": coping_tips,
            "music_recommendations": music_recommendations,
            "red_flags": red_flags,
            "positive_signals": positive_signals,
            "follow_up_actions": follow_up_actions,
        }

    # ========================================================
    # SIGNAL EXTRACTION
    # ========================================================

    def _extract_user_signals(
        self,
        assessment_answers: Dict[str, Any],
        profile_answers: Dict[str, Any],
        predictions: Dict[str, Any],
        combined_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Central place to normalize important signals from the assessment form.
        This lets recommendation rules stay clean.
        """

        # ---------- common academic / mental health inputs ----------
        study_hours = _to_float(assessment_answers.get("study_hours_per_day"))
        exam_pressure = _to_float(assessment_answers.get("exam_pressure"))
        stress_level = _to_float(assessment_answers.get("stress_level"))
        anxiety_score = _to_float(assessment_answers.get("anxiety_score"))
        depression_score = _to_float(assessment_answers.get("depression_score"))
        sleep_hours = _to_float(assessment_answers.get("sleep_hours"))
        screen_time = _to_float(
            assessment_answers.get("screen_time")
            or assessment_answers.get("screen_time_hours")
        )
        physical_activity = _to_float(assessment_answers.get("physical_activity"))
        social_support = _to_float(assessment_answers.get("social_support"))
        financial_stress = _to_float(assessment_answers.get("financial_stress"))
        family_expectation = _to_float(assessment_answers.get("family_expectation"))
        academic_performance = _to_float(assessment_answers.get("academic_performance"))
        internet_usage = _to_float(assessment_answers.get("internet_usage"))
        burnout_score = _to_float(combined_summary.get("burnout_score"))
        wellness_score = _to_float(combined_summary.get("wellness_score"))

        # ---------- music / mxmh related ----------
        fav_genre = _safe_lower(
            assessment_answers.get("fav_genre")
            or assessment_answers.get("music_genre")
            or assessment_answers.get("preferred_genre")
        )

        hours_per_day_music = _to_float(
            assessment_answers.get("hours_per_day")
            or assessment_answers.get("music_hours_per_day")
        )

        while_working = _bool_like(assessment_answers.get("while_working"))
        exploratory = _bool_like(assessment_answers.get("exploratory"))
        foreign_languages = _bool_like(assessment_answers.get("foreign_languages"))
        instrumentalist = _bool_like(assessment_answers.get("instrumentalist"))
        composer = _bool_like(assessment_answers.get("composer"))

        insomnia = _to_float(assessment_answers.get("insomnia"))
        ocd = _to_float(assessment_answers.get("ocd"))

        # ---------- survey style / stress dataset signals ----------
        recent_stress = _to_float(assessment_answers.get("recent_stress"))
        rapid_heartbeat = _to_float(assessment_answers.get("rapid_heartbeat"))
        headaches = _to_float(assessment_answers.get("headaches"))
        irritability = _to_float(assessment_answers.get("irritability"))
        concentration_issues = _to_float(assessment_answers.get("concentration_issues"))
        sadness = _to_float(assessment_answers.get("sadness"))
        loneliness = _to_float(assessment_answers.get("loneliness"))
        academic_overwhelm = _to_float(assessment_answers.get("academic_overwhelm"))
        leisure_difficulty = _to_float(assessment_answers.get("leisure_difficulty"))
        confidence_issues = _to_float(assessment_answers.get("confidence_issues"))

        # ---------- profile side ----------
        age = _to_int(profile_answers.get("age") or assessment_answers.get("age"))
        gender = _safe_lower(profile_answers.get("gender") or assessment_answers.get("gender"))
        academic_year = _to_int(
            profile_answers.get("academic_year") or assessment_answers.get("academic_year")
        )

        # ---------- derived boolean risk flags ----------
        poor_sleep = sleep_hours > 0 and sleep_hours < 6
        severe_sleep_loss = sleep_hours > 0 and sleep_hours < 5
        high_screen_time = screen_time >= 8
        low_physical_activity = physical_activity > 0 and physical_activity < 2
        low_social_support = social_support > 0 and social_support < 4
        high_exam_pressure = exam_pressure >= 7
        high_stress = stress_level >= 7
        high_anxiety = anxiety_score >= 7
        high_depression = depression_score >= 7
        high_financial_stress = financial_stress >= 7
        high_family_expectation = family_expectation >= 7
        heavy_music_usage = hours_per_day_music >= 5
        sleep_issue_music_user = insomnia >= 6 if insomnia else False

        return {
            # profile
            "age": age,
            "gender": gender,
            "academic_year": academic_year,

            # assessment numeric
            "study_hours": study_hours,
            "exam_pressure": exam_pressure,
            "stress_level": stress_level,
            "anxiety_score": anxiety_score,
            "depression_score": depression_score,
            "sleep_hours": sleep_hours,
            "screen_time": screen_time,
            "physical_activity": physical_activity,
            "social_support": social_support,
            "financial_stress": financial_stress,
            "family_expectation": family_expectation,
            "academic_performance": academic_performance,
            "internet_usage": internet_usage,

            # prediction scores
            "burnout_score": burnout_score,
            "wellness_score": wellness_score,

            # music
            "fav_genre": fav_genre,
            "hours_per_day_music": hours_per_day_music,
            "while_working": while_working,
            "exploratory": exploratory,
            "foreign_languages": foreign_languages,
            "instrumentalist": instrumentalist,
            "composer": composer,
            "insomnia": insomnia,
            "ocd": ocd,

            # stress dataset style
            "recent_stress": recent_stress,
            "rapid_heartbeat": rapid_heartbeat,
            "headaches": headaches,
            "irritability": irritability,
            "concentration_issues": concentration_issues,
            "sadness": sadness,
            "loneliness": loneliness,
            "academic_overwhelm": academic_overwhelm,
            "leisure_difficulty": leisure_difficulty,
            "confidence_issues": confidence_issues,

            # derived booleans
            "poor_sleep": poor_sleep,
            "severe_sleep_loss": severe_sleep_loss,
            "high_screen_time": high_screen_time,
            "low_physical_activity": low_physical_activity,
            "low_social_support": low_social_support,
            "high_exam_pressure": high_exam_pressure,
            "high_stress": high_stress,
            "high_anxiety": high_anxiety,
            "high_depression": high_depression,
            "high_financial_stress": high_financial_stress,
            "high_family_expectation": high_family_expectation,
            "heavy_music_usage": heavy_music_usage,
            "sleep_issue_music_user": sleep_issue_music_user,
        }

    # ========================================================
    # SELF CARE PLAN
    # ========================================================

    def _build_self_care_plan(
        self,
        user_signals: Dict[str, Any],
        burnout_band: Optional[str],
        wellness_band: Optional[str],
        overall_risk_level: Optional[str],
    ) -> List[Dict[str, Any]]:
        plans: List[Dict[str, Any]] = []

        poor_sleep = user_signals["poor_sleep"]
        severe_sleep_loss = user_signals["severe_sleep_loss"]
        high_screen_time = user_signals["high_screen_time"]
        low_physical_activity = user_signals["low_physical_activity"]
        high_exam_pressure = user_signals["high_exam_pressure"]
        low_social_support = user_signals["low_social_support"]

        # 1) Sleep recovery
        if poor_sleep:
            plans.append({
                "title": "Sleep Recovery Plan",
                "priority": "high" if severe_sleep_loss else "medium",
                "why": "Your responses suggest insufficient sleep, which can worsen stress, concentration, mood, and burnout.",
                "actions": [
                    "Aim for a consistent sleep window for the next 7 days.",
                    "Avoid heavy screen use 45–60 minutes before bedtime.",
                    "Keep caffeine intake lower in the evening.",
                    "Use a calming pre-sleep routine: low light, light stretching, or calm music."
                ]
            })

        # 2) Burnout recovery
        if _safe_lower(burnout_band) == "high":
            plans.append({
                "title": "Burnout Recovery Plan",
                "priority": "high",
                "why": "Your burnout pattern suggests ongoing emotional or academic exhaustion.",
                "actions": [
                    "Reduce non-essential workload for the next few days where possible.",
                    "Break study tasks into smaller blocks instead of long sessions.",
                    "Schedule at least one guilt-free rest block daily.",
                    "Track 1–2 major stress triggers and remove one avoidable trigger this week."
                ]
            })
        elif _safe_lower(burnout_band) == "moderate":
            plans.append({
                "title": "Burnout Prevention Plan",
                "priority": "medium",
                "why": "You may be showing early signs of burnout or sustained pressure.",
                "actions": [
                    "Use shorter study cycles with recovery breaks.",
                    "Avoid stacking multiple heavy academic tasks in one sitting.",
                    "Set a realistic daily study cap instead of overextending.",
                    "Take a quick check-in every evening: stress, energy, sleep, focus."
                ]
            })

        # 3) Screen time management
        if high_screen_time:
            plans.append({
                "title": "Digital Overload Reduction",
                "priority": "medium",
                "why": "High screen exposure can contribute to fatigue, sleep disruption, and reduced attention recovery.",
                "actions": [
                    "Take a 5-minute eye/body break after every 45–60 minutes of screen use.",
                    "Move non-essential scrolling away from late-night hours.",
                    "Keep at least one short no-screen block daily.",
                    "Use music/audio instead of passive scrolling during breaks."
                ]
            })

        # 4) Activity / energy restoration
        if low_physical_activity:
            plans.append({
                "title": "Energy Reset Through Movement",
                "priority": "medium",
                "why": "Low physical activity can make stress recovery, mood regulation, and sleep quality harder.",
                "actions": [
                    "Add a 10–20 minute walk or light movement session most days.",
                    "Do brief movement between study sessions.",
                    "Use activity as a reset after stressful academic blocks.",
                    "Keep the goal realistic: consistency matters more than intensity."
                ]
            })

        # 5) Academic pressure support
        if high_exam_pressure:
            plans.append({
                "title": "Academic Pressure Stabilization",
                "priority": "high" if _safe_lower(overall_risk_level) == "high" else "medium",
                "why": "Exam pressure appears to be a meaningful stress driver for you.",
                "actions": [
                    "List all current academic tasks and rank them by urgency + marks impact.",
                    "Start with the smallest high-impact task to regain control.",
                    "Use a revision plan with time blocks instead of studying reactively.",
                    "Keep one buffer slot daily for spillover or revision."
                ]
            })

        # 6) Social support
        if low_social_support:
            plans.append({
                "title": "Support Activation Plan",
                "priority": "medium",
                "why": "Lower support can make academic and emotional stress feel heavier.",
                "actions": [
                    "Reach out to one trusted friend, sibling, or mentor this week.",
                    "Avoid isolating when stress is rising.",
                    "If available, consider talking to a counselor, faculty mentor, or support person.",
                    "Share one specific difficulty instead of saying only 'I’m stressed'."
                ]
            })

        # Fallback plan if nothing triggered strongly
        if not plans:
            plans.append({
                "title": "Wellness Maintenance Plan",
                "priority": "low",
                "why": "Your responses do not show one single dominant risk area, so the goal is maintaining stability.",
                "actions": [
                    "Keep a regular sleep schedule.",
                    "Continue balancing study and recovery time.",
                    "Use music, breaks, and movement to prevent overload.",
                    "Track stress changes weekly rather than waiting for a crisis point."
                ]
            })

        return plans

    # ========================================================
    # COPING TIPS
    # ========================================================

    def _build_coping_tips(
        self,
        user_signals: Dict[str, Any],
        stress_type_prediction: Optional[str],
        mental_health_status: Optional[str],
    ) -> List[Dict[str, Any]]:
        tips: List[Dict[str, Any]] = []

        high_anxiety = user_signals["high_anxiety"]
        high_depression = user_signals["high_depression"]
        concentration_issues = user_signals["concentration_issues"] >= 3
        irritability = user_signals["irritability"] >= 3
        loneliness = user_signals["loneliness"] >= 3

        # Anxiety-focused
        if high_anxiety or "distress" in _safe_lower(stress_type_prediction):
            tips.append({
                "category": "anxiety regulation",
                "tip": "Use a short grounding reset when stress spikes: slow breathing + naming 5 things you can see around you.",
                "reason": "This helps interrupt fast escalation of tension and racing thoughts."
            })

        # Low mood / depressive signals
        if high_depression or "at risk" in _safe_lower(mental_health_status):
            tips.append({
                "category": "low mood support",
                "tip": "Use very small action targets on low-energy days—one chapter, one summary page, one 10-minute task.",
                "reason": "Small wins reduce overwhelm and help maintain momentum when mood is low."
            })

        # Concentration
        if concentration_issues:
            tips.append({
                "category": "focus support",
                "tip": "Try 25–40 minute focused study blocks with a fixed single task and a short break after each block.",
                "reason": "Structured blocks are often easier to sustain than long unstructured study sessions."
            })

        # Irritability / overload
        if irritability:
            tips.append({
                "category": "overload management",
                "tip": "When irritation rises, step away for 5 minutes instead of forcing through the task.",
                "reason": "Short interruption prevents stress from turning into mental exhaustion or unproductive study time."
            })

        # Loneliness
        if loneliness:
            tips.append({
                "category": "social coping",
                "tip": "Schedule one low-pressure check-in with someone you trust rather than waiting until stress becomes overwhelming.",
                "reason": "Early connection often reduces emotional load more effectively than late crisis sharing."
            })

        # Generic fallback
        if not tips:
            tips.extend([
                {
                    "category": "daily regulation",
                    "tip": "Keep one fixed recovery habit daily: walk, music break, journaling, or breathing exercise.",
                    "reason": "Consistency in one recovery habit is often more effective than many random strategies."
                },
                {
                    "category": "study balance",
                    "tip": "Plan tomorrow’s top 3 tasks before ending today’s study session.",
                    "reason": "This reduces uncertainty and helps your mind switch off more easily."
                }
            ])

        return tips

    # ========================================================
    # MUSIC RECOMMENDATIONS
    # ========================================================

    def _build_music_recommendations(
        self,
        user_signals: Dict[str, Any],
        music_effect_prediction: Optional[str],
        stress_type_prediction: Optional[str],
    ) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []

        fav_genre = user_signals["fav_genre"]
        high_anxiety = user_signals["high_anxiety"]
        high_depression = user_signals["high_depression"]
        poor_sleep = user_signals["poor_sleep"]
        while_working = user_signals["while_working"]
        heavy_music_usage = user_signals["heavy_music_usage"]

        effect = _safe_lower(music_effect_prediction)
        stress_type = _safe_lower(stress_type_prediction)

        # ----------------------------------------------------
        # CASE 1: Music predicted to help
        # ----------------------------------------------------
        if effect == "improve":
            if poor_sleep:
                recommendations.append({
                    "context": "sleep support",
                    "suggested_genres": ["lofi", "classical", "ambient / soft instrumental"],
                    "why": "Your profile suggests sleep strain, so lower-intensity and calmer listening may be more useful during evening wind-down."
                })

            if high_anxiety or "distress" in stress_type:
                recommendations.append({
                    "context": "anxiety reduction",
                    "suggested_genres": ["lofi", "classical", "soft jazz", "instrumental"],
                    "why": "Calmer and lower-intensity listening is often better suited for anxiety regulation than highly stimulating tracks."
                })

            if while_working:
                recommendations.append({
                    "context": "study / work focus",
                    "suggested_genres": ["lofi", "video game music", "instrumental electronic", "soft ambient"],
                    "why": "You indicated music use while working, so structured background music may support focus without demanding too much attention."
                })

            if high_depression and not poor_sleep:
                recommendations.append({
                    "context": "mood lift",
                    "suggested_genres": ["pop", "r&b", "uplifting hip hop", "light edm"],
                    "why": "If music generally helps you, slightly more energizing but emotionally safe genres may help with activation and mood lifting."
                })

        # ----------------------------------------------------
        # CASE 2: Music predicted neutral
        # ----------------------------------------------------
        elif effect == "no effect":
            recommendations.append({
                "context": "music as optional support",
                "suggested_genres": [fav_genre] if fav_genre else ["lofi", "instrumental", "soft pop"],
                "why": "Music may not strongly improve or worsen your mental state, so use it mainly as a comfort/focus tool rather than your only coping strategy."
            })

        # ----------------------------------------------------
        # CASE 3: Music predicted worsen
        # ----------------------------------------------------
        elif effect == "worsen":
            recommendations.append({
                "context": "careful music use",
                "suggested_genres": ["low-intensity instrumental", "soft lofi", "calm acoustic"],
                "why": "Your profile suggests that music may not always help. Try lower-intensity listening and avoid using emotionally intense music during high-stress periods."
            })
            recommendations.append({
                "context": "non-music coping backup",
                "suggested_genres": [],
                "why": "Because music may worsen your state in some contexts, pair it with non-music strategies like movement, breathing, journaling, or talking to someone."
            })

        # ----------------------------------------------------
        # Generic personalization based on current genre
        # ----------------------------------------------------
        if fav_genre:
            recommendations.append({
                "context": "personalization",
                "suggested_genres": [fav_genre],
                "why": f"You already seem drawn to {fav_genre.title()}, so if that genre feels emotionally safe for you, it can remain part of your support routine."
            })

        # ----------------------------------------------------
        # Heavy music usage note
        # ----------------------------------------------------
        if heavy_music_usage:
            recommendations.append({
                "context": "healthy music use",
                "suggested_genres": [],
                "why": "You seem to use music heavily. That can be helpful, but avoid using it as the only coping strategy—combine it with sleep, breaks, movement, and support."
            })

        if not recommendations:
            recommendations.append({
                "context": "general music support",
                "suggested_genres": ["lofi", "classical", "soft pop"],
                "why": "These are safer default choices when the goal is calm focus or low-stimulation recovery."
            })

        return recommendations

    # ========================================================
    # RED FLAGS
    # ========================================================

    def _build_red_flags(
        self,
        user_signals: Dict[str, Any],
        burnout_band: Optional[str],
        mental_health_status: Optional[str],
        overall_risk_level: Optional[str],
    ) -> List[str]:
        red_flags: List[str] = []

        if user_signals["severe_sleep_loss"]:
            red_flags.append("Sleep duration appears significantly low, which can strongly worsen stress, mood, and concentration.")

        if user_signals["high_anxiety"]:
            red_flags.append("Your anxiety-related responses appear elevated.")

        if user_signals["high_depression"]:
            red_flags.append("Your low-mood / depression-related responses appear elevated.")

        if _safe_lower(burnout_band) == "high":
            red_flags.append("Your burnout risk appears high, suggesting sustained academic or emotional exhaustion.")

        if user_signals["low_social_support"]:
            red_flags.append("Lower social support may make recovery from stress harder.")

        if user_signals["high_exam_pressure"]:
            red_flags.append("Exam or academic pressure appears to be a major stress driver.")

        if "at risk" in _safe_lower(mental_health_status):
            red_flags.append("Mental health classification suggests elevated vulnerability and should be taken seriously.")

        if _safe_lower(overall_risk_level) == "high":
            red_flags.append("Your combined risk pattern appears elevated across multiple areas rather than only one.")

        return red_flags

    # ========================================================
    # POSITIVE SIGNALS
    # ========================================================

    def _build_positive_signals(
        self,
        user_signals: Dict[str, Any],
        burnout_band: Optional[str],
        wellness_band: Optional[str],
    ) -> List[str]:
        positives: List[str] = []

        if user_signals["sleep_hours"] >= 7:
            positives.append("Your sleep duration looks relatively supportive.")

        if user_signals["physical_activity"] >= 3:
            positives.append("Your physical activity level may support better stress recovery.")

        if user_signals["social_support"] >= 6:
            positives.append("You appear to have meaningful social support, which is a strong protective factor.")

        if _safe_lower(burnout_band) == "low":
            positives.append("Your burnout risk currently appears low.")

        if _safe_lower(wellness_band) == "good":
            positives.append("Your wellness indicators look relatively stable.")

        if user_signals["academic_performance"] >= 70:
            positives.append("Your academic performance indicators appear reasonably stable.")

        return positives

    # ========================================================
    # FOLLOW UP ACTIONS
    # ========================================================

    def _build_follow_up_actions(
        self,
        user_signals: Dict[str, Any],
        burnout_band: Optional[str],
        wellness_band: Optional[str],
        mental_health_status: Optional[str],
        overall_risk_level: Optional[str],
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        high_risk = _safe_lower(overall_risk_level) == "high"
        at_risk = "at risk" in _safe_lower(mental_health_status)
        burnout_high = _safe_lower(burnout_band) == "high"

        # urgent-ish support recommendation
        if high_risk or at_risk or burnout_high:
            actions.append({
                "priority": "high",
                "action": "Consider speaking to a counselor, trusted mentor, or mental health professional if these patterns are affecting your daily functioning.",
                "reason": "Your responses suggest elevated stress / burnout / emotional risk across one or more areas."
            })

        # sleep follow-up
        if user_signals["poor_sleep"]:
            actions.append({
                "priority": "medium",
                "action": "Track sleep for the next 7 days and check whether stress, screen time, or late study hours are the main cause.",
                "reason": "Sleep appears to be one of the areas most likely to influence your overall mental state."
            })

        # academic overload follow-up
        if user_signals["high_exam_pressure"] or user_signals["academic_overwhelm"] >= 3:
            actions.append({
                "priority": "medium",
                "action": "Create a weekly academic load plan with task prioritization rather than reacting day-by-day.",
                "reason": "Your responses suggest that workload organization may reduce stress significantly."
            })

        # support follow-up
        if user_signals["low_social_support"]:
            actions.append({
                "priority": "medium",
                "action": "Identify one person you can realistically reach out to this week for support.",
                "reason": "Social support is one of the strongest buffers against academic stress and burnout."
            })

        # wellness maintenance
        if not actions:
            actions.append({
                "priority": "low",
                "action": "Repeat the assessment after a few weeks or after a major academic stress period to track changes.",
                "reason": "Your current profile does not show a single urgent intervention need, so monitoring and prevention are appropriate."
            })

        return actions


# ============================================================
# SINGLETON + PUBLIC FUNCTION
# ============================================================

recommendation_engine = RecommendationEngine()


def generate_recommendations(
    assessment_answers: Dict[str, Any],
    profile_answers: Optional[Dict[str, Any]] = None,
    prediction_bundle: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Public function used by ml_engine.py
    """
    return recommendation_engine.generate(
        assessment_answers=assessment_answers,
        profile_answers=profile_answers or {},
        prediction_bundle=prediction_bundle or {},
    )