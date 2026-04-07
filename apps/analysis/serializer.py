from rest_framework import serializers
from yt_insight_current.apps.analysis.models.models import YoutubeAnalysis

class AnalysisInputSerializer(serializers.Serializer):
    channel_url = serializers.URLField()

class AnalysisOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeAnalysis
        fields = (
            "id",
            "youtube_id",
            "youtube_type"
            "title",
            "summary",
            "created_at"
        )