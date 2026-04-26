from django.db import models


class StatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class SentimentChoices(models.TextChoices):
    POSITIVE = "positive", "Positive"
    NEGATIVE = "negative", "Negative"
    MIXED = "mixed", "Mixed"
    NEUTRAL = "neutral", "Neutral"


class CategoryChoices(models.TextChoices):
    CONTENT = "content", "Content"
    ENGAGEMENT = "engagement", "Engagement"
    GROWTH = "growth", "Growth"
    MONETIZATION = "monetization", "Monetization"
    AUDIENCE = "audience", "Audience"
    CUSTOM = "custom", "Custom"
