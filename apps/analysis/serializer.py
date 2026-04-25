from rest_framework import serializers

from apps.analysis.models import (
    Analysis,
    AnalysisResult,
    AnalysisTopic,
    AnalysisQuestion,
    AnalysisSuggestion,
    Channel,
)


class AnalysisInputSerializer(serializers.Serializer):
    channel_url = serializers.URLField()


# ── Nested read-only serializers ───────────────────────────────────────────────

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            "youtube_channel_id",
            "title",
            "description",
            "thumbnail_url",
            "subscriber_count",
            "video_count",
        )


class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = ("summary", "sentiment", "audience_type")


class AnalysisTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisTopic
        fields = ("topic", "relevance_score")


class AnalysisQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisQuestion
        fields = ("question", "answer", "category")


class AnalysisSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisSuggestion
        fields = ("suggestion", "category")


# ── Response serializers ───────────────────────────────────────────────────────

class AnalysisStatusSerializer(serializers.ModelSerializer):
    """Lightweight — used for 202 response and polling."""

    class Meta:
        model = Analysis
        fields = ("id", "status", "videos_analyzed", "comments_analyzed", "error_message", "created_at")


class AnalysisListSerializer(serializers.ModelSerializer):
    """Summary view for the list endpoint — no nested result data."""
    channel = ChannelSerializer(read_only=True)

    class Meta:
        model = Analysis
        fields = (
            "id",
            "input_url",
            "status",
            "videos_analyzed",
            "comments_analyzed",
            "channel",
            "created_at",
        )


class AnalysisDetailSerializer(serializers.ModelSerializer):
    """Full detail view including all AI-generated results."""
    channel = ChannelSerializer(read_only=True)
    result = AnalysisResultSerializer(read_only=True)
    topics = AnalysisTopicSerializer(many=True, read_only=True)
    questions = AnalysisQuestionSerializer(many=True, read_only=True)
    suggestions = AnalysisSuggestionSerializer(many=True, read_only=True)

    class Meta:
        model = Analysis
        fields = (
            "id",
            "input_url",
            "status",
            "videos_analyzed",
            "comments_analyzed",
            "error_message",
            "channel",
            "result",
            "topics",
            "questions",
            "suggestions",
            "created_at",
        )
