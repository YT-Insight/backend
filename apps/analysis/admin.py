from django.contrib import admin
from .models import (
    Channel, Video, Analysis, AnalysisVideo,
    AnalysisResult, AnalysisTopic, AnalysisQuestion, AnalysisSuggestion,
)
from .models.youtube import Comment


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("title", "youtube_channel_id", "subscriber_count", "video_count", "created_at")
    search_fields = ("title", "youtube_channel_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "channel", "view_count", "comment_count", "published_at")
    search_fields = ("title", "youtube_video_id")
    list_filter = ("channel",)
    readonly_fields = ("created_at", "updated_at")


class AnalysisVideoInline(admin.TabularInline):
    model = AnalysisVideo
    extra = 0
    readonly_fields = ("video", "comments_fetched", "created_at")
    can_delete = False


class AnalysisResultInline(admin.StackedInline):
    model = AnalysisResult
    extra = 0
    readonly_fields = ("summary", "sentiment", "audience_type")
    can_delete = False


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "channel", "status", "videos_analyzed", "comments_analyzed", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "channel__title", "input_url")
    readonly_fields = ("created_at", "updated_at")
    inlines = [AnalysisVideoInline, AnalysisResultInline]


@admin.register(AnalysisTopic)
class AnalysisTopicAdmin(admin.ModelAdmin):
    list_display = ("topic", "relevance_score", "analysis")
    list_filter = ("analysis__status",)
    readonly_fields = ("created_at",)


@admin.register(AnalysisQuestion)
class AnalysisQuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "analysis")
    list_filter = ("category",)
    readonly_fields = ("created_at",)


@admin.register(AnalysisSuggestion)
class AnalysisSuggestionAdmin(admin.ModelAdmin):
    list_display = ("suggestion", "category", "analysis")
    list_filter = ("category",)
    readonly_fields = ("created_at",)
