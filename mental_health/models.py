from django.db import models

from django.contrib.auth.models import User


class MoodEntry(models.Model):

    MOOD_CHOICES = [

        ('happy', 'Happy'),

        ('sad', 'Sad'),

        ('anxious', 'Anxious'),

        ('stressed', 'Stressed'),

        ('neutral', 'Neutral'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
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

    sleep_hours = models.FloatField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.user.username} - {self.emotion}"