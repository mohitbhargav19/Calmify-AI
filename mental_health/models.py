from django.db import models
from django.contrib.auth.models import User


# =====================================
# Mood Tracking
# =====================================

class MoodEntry(models.Model):

    MOOD_CHOICES = [
        ("happy", "Happy"),
        ("sad", "Sad"),
        ("anxious", "Anxious"),
        ("stressed", "Stressed"),
        ("neutral", "Neutral"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mood_entries"
    )

    mood_score = models.IntegerField()

    emotion = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES
    )

    journal_text = models.TextField(
        blank=True,
        null=True
    )

    sleep_hours = models.FloatField(
        default=7
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.emotion}"


# =====================================
# Assessment
# =====================================

class Assessment(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assessments"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Assessment #{self.id} - {self.user.username}"


class AssessmentAnswer(models.Model):

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question_id = models.IntegerField()

    category = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    answer_text = models.CharField(
        max_length=255
    )

    answer_score = models.IntegerField()

    def __str__(self):
        return f"Q{self.question_id} - {self.answer_score}"


# =====================================
# User Profile
# =====================================

class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    age = models.IntegerField()

    gender = models.CharField(
        max_length=20
    )

    academic_year = models.IntegerField(
        default=1
    )

    cgpa = models.FloatField(
        default=0
    )

    course = models.CharField(
        max_length=100,
        default=""
    )

    residence_type = models.CharField(
        max_length=100,
        default=""
    )

    internet_usage = models.FloatField(
        default=0
    )

    daily_steps = models.IntegerField(
        default=0
    )

    sleep_hours = models.FloatField(
        default=7
    )

    physical_activity = models.IntegerField(
        default=3
    )

    social_support = models.IntegerField(
        default=3
    )

    financial_stress = models.IntegerField(
        default=3
    )

    family_expectation = models.IntegerField(
        default=3
    )

    screen_time = models.FloatField(
        default=4
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username


# =====================================
# User Preferences
# =====================================

class UserPreference(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    favorite_music = models.JSONField(
        default=list
    )

    favorite_activities = models.JSONField(
        default=list
    )

    primary_goal = models.CharField(
        max_length=100,
        default="Improve Mental Wellness"
    )

    def __str__(self):
        return self.user.username


# =====================================
# Prediction
# =====================================

class Prediction(models.Model):

    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        related_name="prediction"
    )

    stress_level = models.CharField(
        max_length=50
    )

    burnout_level = models.CharField(
        max_length=50
    )

    sleep_quality = models.CharField(
        max_length=50
    )

    wellness_score = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Prediction #{self.id}"


# =====================================
# Dashboard Results
# =====================================

class DashboardResult(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dashboard_results"
    )

    stress_level = models.IntegerField()

    stress_type = models.IntegerField()

    burnout_score = models.FloatField()

    mental_health_status = models.IntegerField()

    wellness_score = models.FloatField()

    recommendations = models.JSONField(
        default=dict
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Dashboard Result #{self.id}"


# =====================================
# Recommendation
# =====================================

class Recommendation(models.Model):

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )

    category = models.CharField(
        max_length=50
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    def __str__(self):
        return self.title
    


#=========================
# assessment report
#=========================

class AssessmentReport(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    stress_level = models.IntegerField()

    burnout_score = models.FloatField()

    wellness_score = models.FloatField()

    mental_health_status = models.CharField(
        max_length=100
    )

    recommended_music = models.JSONField(
        default=list
    )

    recommended_activities = models.JSONField(
        default=list
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.user.username}"
            f" - {self.created_at.date()}"
        )