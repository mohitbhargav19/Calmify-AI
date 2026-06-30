from django.contrib import admin

from .models import (
    MoodEntry,
    Assessment,
    AssessmentAnswer,
    UserProfile,
    DashboardResult
)


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "emotion",
        "mood_score",
        "created_at"
    )

    list_filter = (
        "emotion",
        "created_at"
    )

    search_fields = (
        "user__username",
        "journal_text"
    )


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "submitted_at"
    )

    search_fields = (
        "user__username",
    )


@admin.register(AssessmentAnswer)
class AssessmentAnswerAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "assessment",
        "question_id",
        "answer_score"
    )

    list_filter = (
        "question_id",
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "age",
        "gender",
        "course",
        "cgpa"
    )

    search_fields = (
        "user__username",
        "course"
    )


@admin.register(DashboardResult)
class DashboardResultAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "stress_level",
        "stress_type",
        "burnout_score",
        "wellness_score",
        "created_at"
    )

    list_filter = (
        "created_at",
    )


from django.contrib import admin
from .models import AssessmentReport

admin.site.register(AssessmentReport)