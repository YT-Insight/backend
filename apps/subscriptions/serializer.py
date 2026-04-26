from rest_framework import serializers
from .models import Subscription, UsageLimit


class PlanTierSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    price_cents = serializers.IntegerField()
    price_display = serializers.CharField()
    price_period = serializers.CharField()
    video_limit = serializers.IntegerField()
    highlighted = serializers.BooleanField()
    features = serializers.ListField(child=serializers.CharField())


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("plan", "status", "current_period_end", "stripe_subscription_id")
        read_only_fields = ("plan", "status", "current_period_end", "stripe_subscription_id")


class UsageLimitSerializer(serializers.ModelSerializer):
    percentage_used = serializers.SerializerMethodField()

    class Meta:
        model = UsageLimit
        fields = ("video_analyzed", "video_limit", "reset_at", "percentage_used")
        read_only_fields = ("video_analyzed", "video_limit", "reset_at", "percentage_used")

    def get_percentage_used(self, obj) -> int:
        if obj.video_limit == 0:
            return 100
        return min(100, round((obj.video_analyzed / obj.video_limit) * 100))
