from django.db import models
from apps.common.models import BaseModel


class Channel(BaseModel):
    youtube_channel_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    subscriber_count = models.BigIntegerField(default=0)
    video_count = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["youtube_channel_id"])]

    def __str__(self):
        return self.title


class Video(BaseModel):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    youtube_video_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    view_count = models.BigIntegerField(null=True, blank=True)
    like_count = models.BigIntegerField(null=True, blank=True)
    comment_count = models.BigIntegerField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    thumbnail_url = models.URLField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["youtube_video_id"])]

    def __str__(self):
        return self.title


class Comment(BaseModel):
    analysis_video = models.ForeignKey(
        "analysis.AnalysisVideo",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    author = models.CharField(max_length=255, blank=True)
    like_count = models.IntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.text[:80]
