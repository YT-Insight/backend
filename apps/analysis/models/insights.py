from django.db import models

from apps.common.models import BaseModel
from apps.analysis.models.enums import (
    SentimentChoices,
    CategoryChoices
)


class AnalysisResult(BaseModel):
    analysis = models.OneToOneField(
        "Analysis",
        on_delete=models.CASCADE,
        related_name="result"
    )
    summary = models.TextField(blank=True)
    sentiment = models.CharField(
        max_length=20,
        choices=SentimentChoices.choices,
        default=SentimentChoices.NEUTRAL
    )
    audience_type = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Result for {self.analysis}"


class AnalysisTopic(BaseModel):
    analysis = models.ForeignKey(
        "Analysis",
        on_delete=models.CASCADE,
        related_name="topics"
    )
    topic = models.CharField(max_length=255)
    relevance_score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.topic


class AnalysisQuestion(BaseModel):
    analysis = models.ForeignKey(
        "Analysis",
        on_delete=models.CASCADE,
        related_name="questions"
    )
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    category = models.CharField(
        max_length=255,
        choices=CategoryChoices.choices,
        blank=True
    )

    def __str__(self):
        return self.question


class AnalysisSuggestion(BaseModel):
    analysis = models.ForeignKey(
        "Analysis",
        on_delete=models.CASCADE,
        related_name="suggestions"
    )
    suggestion = models.TextField()
    category = models.CharField(
        max_length=255,
        choices=CategoryChoices.choices,
        blank=True
    )

    def __str__(self):
        return self.suggestion[:50]