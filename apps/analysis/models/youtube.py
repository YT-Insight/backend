from django.db import models
from apps.common.models import BaseModel


class Channel(BaseModel):
    youtube_channel_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    subscriber_count = models.BigIntegerField()
    video_count = models.IntegerField()

    def __str__(self):
        return self.title


class Video(BaseModel):
    channel = models.ForeignKey(
        "Channel",
        on_delete=models.CASCADE,
        related_name="videos"
    )
    youtube_video_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="The unique identifier for the YouTube video."
    )
    title = models.CharField(max_length=255)
    view_count = models.BigIntegerField(null=True)
    like_count = models.BigIntegerField(null=True)
    comment_count = models.BigIntegerField(null=True)
    published_at = models.DateTimeField(null=True)
    thumbnail_url = models.URLField(blank=True)

    def __str__(self):
        return self.title