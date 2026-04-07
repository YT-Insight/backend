from rest_framework import serializers
from apps.analysis.models import YoutubeAnalysis

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