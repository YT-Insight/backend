from apps.analysis.services.youtube_client import get_channel_info
from yt_insight_current.apps.analysis.models.models import YoutubeAnalysis
from apps.analysis.services.ai_service import analyze_channel

def run_analysis(user, channel_url: str) -> dict:
    channel_info = get_channel_info(channel_url) # gets channel info(youtube api) but for now it is just mock

    existing = YoutubeAnalysis.objects.filter(
        user=user,
        youtube_id=channel_info["channel_info"]
    ).first()

    if existing: return existing

    summary = analyze_channel(channel_info)

    analysis = YoutubeAnalysis.objects.create(
        user=user,
        youtube_type="channel",
        youtube_id=channel_info["channel_id"],
        title=channel_info["title"],
        summary=summary,
    )
