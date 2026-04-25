from django.contrib import admin
from .models import Subscription, UsageLimit


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "current_period_end", "created_at")
    list_filter = ("plan", "status")
    search_fields = ("user__email", "stripe_subscription_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(UsageLimit)
class UsageLimitAdmin(admin.ModelAdmin):
    list_display = ("user", "video_analyzed", "video_limit", "reset_at")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")
