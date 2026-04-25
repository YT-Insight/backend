import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils.dateparse import parse_datetime

from apps.analysis.models import (
    Analysis,
    AnalysisVideo,
    AnalysisResult,
    AnalysisTopic,
    AnalysisQuestion,
    AnalysisSuggestion,
    Channel,
    Video,
)
from apps.analysis.models.youtube import Comment
from apps.analysis.models.enums import StatusChoices
from apps.analysis.services.youtube_client import YouTubeClient, YouTubeAPIError
from apps.analysis.services.ai_service import analyze_comments

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_analysis_task(self, analysis_id: str):
    """Full pipeline: YouTube fetch → comment storage → AI analysis → result storage."""
    try:
        analysis = Analysis.objects.select_related("user").get(id=analysis_id)
    except Analysis.DoesNotExist:
        logger.error("run_analysis_task called with unknown id: %s", analysis_id)
        return

    try:
        _pipeline(analysis)
    except Exception as exc:
        logger.exception("Analysis %s failed: %s", analysis_id, exc)
        Analysis.objects.filter(id=analysis_id).update(
            status=StatusChoices.FAILED,
            error_message=str(exc),
        )
        raise self.retry(exc=exc)


# ── Pipeline stages ────────────────────────────────────────────────────────────

def _pipeline(analysis: Analysis) -> None:
    Analysis.objects.filter(id=analysis.id).update(status=StatusChoices.PROCESSING)

    client = YouTubeClient(api_key=settings.YOUTUBE_API_KEY)

    # Stage 1 — Resolve and cache channel ─────────────────────────────────────
    channel_id = client.resolve_channel_id(analysis.input_url)
    channel_data = client.get_channel_info(channel_id)
    channel = _upsert_channel(channel_data)

    Analysis.objects.filter(id=analysis.id).update(channel=channel)
    analysis.channel = channel  # keep local ref in sync

    # Stage 2 — Fetch videos ───────────────────────────────────────────────────
    videos_data = client.get_channel_videos(channel_id, max_results=20)
    analysis_videos = _upsert_videos(analysis, channel, videos_data)

    if not analysis_videos:
        _finish(analysis, videos_analyzed=0, comments_analyzed=0)
        return

    # Stage 3 — Fetch comments concurrently ───────────────────────────────────
    all_comment_texts = _fetch_all_comments(client, analysis_videos)

    # Stage 4 — AI analysis ───────────────────────────────────────────────────
    ai_result = analyze_comments(all_comment_texts, {
        "title": channel.title,
        "description": channel.description,
    })

    # Stage 5 — Persist results atomically ───────────────────────────────────
    _store_results(analysis, ai_result)

    # Stage 6 — Finalise ──────────────────────────────────────────────────────
    _finish(analysis, videos_analyzed=len(analysis_videos), comments_analyzed=len(all_comment_texts))
    _increment_usage(analysis.user)

    logger.info(
        "Analysis %s complete: %d videos, %d comments",
        analysis.id, len(analysis_videos), len(all_comment_texts),
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _upsert_channel(data: dict) -> Channel:
    channel_id = data.pop("youtube_channel_id")
    channel, _ = Channel.objects.update_or_create(
        youtube_channel_id=channel_id,
        defaults=data,
    )
    return channel


def _upsert_videos(analysis: Analysis, channel: Channel, videos_data: list[dict]) -> list[AnalysisVideo]:
    analysis_videos: list[AnalysisVideo] = []

    for vd in videos_data:
        video_id = vd.pop("youtube_video_id")
        published_raw = vd.pop("published_at", None)
        published_at = parse_datetime(published_raw) if published_raw else None

        video, _ = Video.objects.update_or_create(
            youtube_video_id=video_id,
            defaults={"channel": channel, "published_at": published_at, **vd},
        )

        av, _ = AnalysisVideo.objects.get_or_create(
            analysis=analysis,
            video=video,
        )
        analysis_videos.append(av)

    return analysis_videos


def _fetch_all_comments(client: YouTubeClient, analysis_videos: list[AnalysisVideo]) -> list[str]:
    all_texts: list[str] = []

    def fetch_one(av: AnalysisVideo) -> list[str]:
        try:
            raw = client.get_video_comments(av.video.youtube_video_id, max_results=300)
        except YouTubeAPIError as exc:
            logger.warning("Skipping comments for video %s: %s", av.video.youtube_video_id, exc)
            return []

        if raw:
            Comment.objects.bulk_create(
                [
                    Comment(
                        analysis_video=av,
                        text=c["text"],
                        author=c.get("author", ""),
                        like_count=c.get("like_count", 0),
                        published_at=parse_datetime(c["published_at"]) if c.get("published_at") else None,
                    )
                    for c in raw
                ]
            )
            AnalysisVideo.objects.filter(pk=av.pk).update(comments_fetched=len(raw))

        return [c["text"] for c in raw]

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fetch_one, av): av for av in analysis_videos}
        for future in as_completed(futures):
            try:
                all_texts.extend(future.result())
            except Exception as exc:
                av = futures[future]
                logger.warning("Comment fetch failed for video %s: %s", av.video.youtube_video_id, exc)

    return all_texts


def _store_results(analysis: Analysis, ai_result: dict) -> None:
    with transaction.atomic():
        AnalysisResult.objects.update_or_create(
            analysis=analysis,
            defaults={
                "summary": ai_result["summary"],
                "sentiment": ai_result["sentiment"],
                "audience_type": ai_result["audience_type"],
            },
        )

        # Replace previous topics / suggestions / questions if this is a retry
        AnalysisTopic.objects.filter(analysis=analysis).delete()
        AnalysisTopic.objects.bulk_create([
            AnalysisTopic(
                analysis=analysis,
                topic=t["topic"],
                relevance_score=t["relevance_score"],
            )
            for t in ai_result["topics"]
        ])

        AnalysisSuggestion.objects.filter(analysis=analysis).delete()
        AnalysisSuggestion.objects.bulk_create([
            AnalysisSuggestion(
                analysis=analysis,
                suggestion=s["suggestion"],
                category=s["category"],
            )
            for s in ai_result["suggestions"]
        ])

        AnalysisQuestion.objects.filter(analysis=analysis).delete()
        AnalysisQuestion.objects.bulk_create([
            AnalysisQuestion(
                analysis=analysis,
                question=q["question"],
                answer=q["answer"],
                category=q["category"],
            )
            for q in ai_result["questions"]
        ])


def _finish(analysis: Analysis, *, videos_analyzed: int, comments_analyzed: int) -> None:
    Analysis.objects.filter(id=analysis.id).update(
        status=StatusChoices.COMPLETED,
        videos_analyzed=videos_analyzed,
        comments_analyzed=comments_analyzed,
        error_message="",
    )


def _increment_usage(user) -> None:
    try:
        user.usage_limit.video_analyzed += 1
        user.usage_limit.save(update_fields=["video_analyzed", "updated_at"])
    except Exception as exc:
        # Usage tracking failure should not roll back the analysis result
        logger.warning("Could not increment usage for user %s: %s", user.id, exc)
