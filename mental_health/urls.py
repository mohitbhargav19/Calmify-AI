from django.urls import path

from .views import (
    home_view,
    assessment_page,
    dashboard_view,
    AssessmentQuestionsView,
    AssessmentSubmitView,
    login_view,
    signup_view,
    logout_view,
)
from .views import download_report

urlpatterns = [

    # ------------------------
    # HTML Pages
    # ------------------------

    path(
        "",
        home_view,
        name="home",
    ),
    
    path(
    "download-report/",
    download_report,
    name="download_report",
    ),

    path(
        "assessment/",
        assessment_page,
        name="assessment_page",
    ),

    path(
        "dashboard/",
        dashboard_view,
        name="dashboard",
    ),

    # ------------------------
    # APIs
    # ------------------------

    path(
    "api/assessment/questions/",
    AssessmentQuestionsView.as_view(),
    name="assessment_questions",
),

path(
    "api/assessment/submit/",
    AssessmentSubmitView.as_view(),
    name="assessment_submit",
),
    
    path(
    "login/",
    login_view,
    name="login",
),

path(
    "signup/",
    signup_view,
    name="signup",
),

path(
    "logout/",
    logout_view,
    name="logout",
),

]
