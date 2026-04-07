from django.db import models


class StatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'


class SentimentChoices(models.TextChoices):
    POSITIVE = 'positive', 'Positive'
    NEGATIVE = 'negative', 'Negative'
    MIXED = 'mixed', 'Mixed'
    NEUTRAL = 'neutral', 'Neutral' 


class CategoryChoices(models.TextChoices):
    SENTIMENT = 'sentiment', 'Sentiment'
    TOPIC = 'topic', 'Topic'
    AUDIENCE = 'audience', 'Audience'
    CUSTOM = 'custom', 'Custom'

class AnalysisSuggestionChoices(models.TextChoices):
    CONTENT = 'content', 'Content'
    ENGAMEMENT = 'engagement', 'Engagement'
    GROWTH = 'growth', 'Growth'
    MONETIZATION = 'monetization', 'Monetization'