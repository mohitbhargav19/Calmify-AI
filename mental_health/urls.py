from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('signup/', views.signup_page, name='signup'),

    path('login/', views.login_page, name='login'),

    path('logout/', views.logout_user, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path(
        'download-report/',
        views.download_report,
        name='download_report'
    ),

    path(
        'moods/',
        views.mood_list,
        name='mood-list'
    ),
]
