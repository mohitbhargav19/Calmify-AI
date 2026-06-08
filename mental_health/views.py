from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import MoodEntry
from .serializers import MoodEntrySerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

from django.http import HttpResponse
from .pdf_utils import generate_report
from django.contrib.auth.decorators import login_required

import json

from .models import MoodEntry

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_user(request):

    logout(request)

    return redirect('/')


from .ai_model import (
    detect_emotion,
    calculate_wellness
)

@api_view(['GET', 'POST'])
def mood_list(request):

    # GET all mood entries
    if request.method == 'GET':
        moods = MoodEntry.objects.all()
        serializer = MoodEntrySerializer(moods, many=True)
        return Response(serializer.data)

    # POST new mood entry
    elif request.method == 'POST':
        serializer = MoodEntrySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render


def home(request):
    return render(request, 'index.html')


def login_page(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/dashboard/')

        else:

            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')

#*******************signup_page

def signup_page(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:

            if User.objects.filter(username=username).exists():

                return render(request, 'signup.html', {
                    'error': 'Username already exists'
                })

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            user.save()

            return redirect('/login/')

        else:

            return render(request, 'signup.html', {
                'error': 'Passwords do not match'
            })

    return render(request, 'signup.html')



#*******************dashboard_page

@login_required
def dashboard(request):

    import json

    # -------------------------------
    # USER MOOD DATA
    # -------------------------------

    moods = MoodEntry.objects.filter(
        user=request.user
    ).order_by('created_at')

    latest_mood = moods.last()

    suggestions = []
    music = []

    # -------------------------------
    # WELLNESS SCORE
    # -------------------------------

    wellness_score = 0

    if latest_mood:

        wellness_score = calculate_wellness(

            latest_mood.mood_score,

            latest_mood.sleep_hours,

            latest_mood.emotion
        )

    # -------------------------------
    # AI SUGGESTIONS
    # -------------------------------

    if latest_mood:

        if latest_mood.mood_score <= 3:

            suggestions.append(
                "Take proper rest and avoid overthinking."
            )

            suggestions.append(
                "Try deep breathing or meditation."
            )

        elif latest_mood.mood_score <= 6:

            suggestions.append(
                "Spend time doing activities you enjoy."
            )

            suggestions.append(
                "Maintain a balanced routine today."
            )

        else:

            suggestions.append(
                "Keep maintaining your positive energy."
            )

            suggestions.append(
                "Share positivity with others today."
            )

        if latest_mood.sleep_hours < 5:

            suggestions.append(
                "Your sleep schedule needs improvement."
            )

        if latest_mood.emotion == "stressed":

            suggestions.append(
                "Take short mindfulness breaks during work."
            )

        elif latest_mood.emotion == "sad":

            suggestions.append(
                "Talk to supportive friends or family."
            )

        elif latest_mood.emotion == "anxious":

            suggestions.append(
                "Practice mindfulness and relaxation."
            )

    # -------------------------------
    # MUSIC RECOMMENDATIONS
    # -------------------------------

    if latest_mood:

        if latest_mood.emotion == "sad":

            music.append(
                "Acoustic Healing Playlist 🎸"
            )

            music.append(
                "Positive Energy Songs ✨"
            )

        elif latest_mood.emotion == "stressed":

            music.append(
                "Deep Focus Lo-fi Beats 🎧"
            )

            music.append(
                "Relaxing Piano Music 🎹"
            )

        elif latest_mood.emotion == "anxious":

            music.append(
                "Meditation Soundscapes 🌙"
            )

            music.append(
                "Nature Calm Sounds 🌿"
            )

        elif latest_mood.emotion == "happy":

            music.append(
                "Feel Good Hits ☀️"
            )

            music.append(
                "Morning Motivation Playlist 🚀"
            )

        else:

            music.append(
                "Balanced Mood Instrumentals 🎼"
            )

    # -------------------------------
    # GRAPH DATA
    # -------------------------------

    mood_scores = []
    sleep_data = []
    dates = []

    for mood in moods:

        mood_scores.append(
            mood.mood_score
        )

        sleep_data.append(
            float(mood.sleep_hours)
        )

        dates.append(
            mood.created_at.strftime("%d %b")
        )

    # -------------------------------
    # MOOD HISTORY
    # -------------------------------

    user_history = MoodEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # -------------------------------
    # WEEKLY SUMMARY
    # -------------------------------

    total_score = 0

    count = user_history.count()

    for mood in user_history:

        total_score += mood.mood_score

    weekly_average = 0

    if count > 0:

        weekly_average = round(
            total_score / count,
            2
        )

    # -------------------------------
    # CONTEXT
    # -------------------------------

    context = {

        'latest_mood': latest_mood,

        'suggestions': suggestions,

        'music': music,

        'wellness_score': wellness_score,

        'mood_scores': json.dumps(
            mood_scores
        ),

        'sleep_data': json.dumps(
            sleep_data
        ),

        'dates': json.dumps(
            dates
        ),

        'user_history': user_history,

        'weekly_average': weekly_average,

        'recent_journals': user_history[:5],
    }

    return render(
        request,
        'dashboard.html',
        context
    )

#*******************
#  download_page
#*******************

@login_required
def download_report(request):

    moods = MoodEntry.objects.filter(
        user=request.user
    ).order_by('created_at')

    latest_mood = moods.last()

    wellness_score = 0

    if latest_mood:

        wellness_score = calculate_wellness(
            latest_mood.mood_score,
            latest_mood.sleep_hours,
            latest_mood.emotion
        )

    total_score = 0

    for mood in moods:

        total_score += mood.mood_score

    weekly_average = 0

    if moods.count() > 0:

        weekly_average = round(
            total_score / moods.count(),
            2
        )

    suggestions = [

        "Maintain healthy sleep habits.",

        "Track your emotions daily.",

        "Listen to recommended music."
    ]

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        'attachment; '
        'filename="Calmify_Report.pdf"'
    )

    generate_report(
        response,
        request.user,
        latest_mood,
        wellness_score,
        weekly_average,
        suggestions
    )

    return response

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_user(request):

    logout(request)

    return redirect('/')