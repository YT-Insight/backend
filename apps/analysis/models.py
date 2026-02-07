from django.db import models
from django.conf import settings
from apps.common.models import BaseModel

# Create your models here.

class YoutubeAnalysis(BaseModel):
    TYPE_CHOICES = [
        ('channel', 'Channel'),
        ('video', 'Video'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analyses')
    youtube_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    youtube_id = models.CharField(max_length=255, help_text="ID of channel or video in Youtube")
    title = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Youtube Analysis'
        verbose_name_plural = 'Youtube Analyses'

        indexes = [
            models.Index(fields=['user', 'youtube_id'])
        ]

    def __str__(self):
        return f"[{self.get_youtube_type_display()}] {self.title or self.youtube_id} by {self.user.email}"
    
class AnalysisQuestion(BaseModel):
    analysis = models.ForeignKey(YoutubeAnalysis, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    answer = models.TextField(blank=True)

    def __str__(self):
        return f"Q: {self.question[:50]}... for Analysis ID: {self.analysis.id}"
    