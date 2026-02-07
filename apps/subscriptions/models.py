from django.db import models
from django.conf import settings
from apps.common.models import BaseModel

# Create your models here.

class Subscription(BaseModel):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Pro'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_period_end = models.DateTimeField(null=True, blank=True)

    def str(self):
        return f"{self.user.email} - {self.get_plan_display()}"
    
class UsageLimit(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usage_limit')
    video_analyzed = models.PositiveIntegerField(default=0)
    video_limit = models.PositiveIntegerField(default=5)
    reset_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - Usage: {self.videos_analyzed}/{self.videos_limit}"
    
    