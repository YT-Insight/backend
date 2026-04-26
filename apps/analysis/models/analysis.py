from django.db import models
from django.conf import settings

from apps.common.models import BaseModel
from apps.analysis.models.enums import StatusChoices


class Analysis(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analyses",
    )
    # Channel is set after the async task resolves it; starts as null
    channel = models.ForeignKey(
        "analysis.Channel",
        on_delete=models.SET_NULL,
        related_name="analyses",
        null=True,
        blank=True,
    )
    input_url = models.URLField()
    videos_analyzed = models.IntegerField(default=0)
    comments_analyzed = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
    )
    error_message = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Analysis #{self.id} — {self.status}"


class AnalysisVideo(BaseModel):
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
        related_name="analysis_videos",
    )
    video = models.ForeignKey(
        "analysis.Video",
        on_delete=models.CASCADE,
        related_name="analysis_videos",
    )
    comments_fetched = models.IntegerField(default=0)

    class Meta:
        unique_together = ("analysis", "video")

    def __str__(self):
        return f"{self.analysis_id} / {self.video_id}"
