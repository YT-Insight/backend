from rest_framework import serializers
from .models import Subscription, UsageLimit


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("plan", "status", "current_period_end", "stripe_subscription_id")
        extra_kwargs = {"stripe_subscription_id": {"read_only": True}}


class UsageLimitSerializer(serializers.ModelSerializer):
    percentage_used = serializers.SerializerMethodField()

    class Meta:
        model = UsageLimit
        fields = ("video_analyzed", "video_limit", "reset_at", "percentage_used")

    def get_percentage_used(self, obj) -> int:
        if obj.video_limit == 0:
            return 100
        return min(100, round((obj.video_analyzed / obj.video_limit) * 100))
