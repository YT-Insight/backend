import re
from rest_framework.exceptions import ValidationError

from apps.analysis.models import Analysis
from apps.analysis.models.enums import StatusChoices
from apps.common.exceptions import QuotaExceededError

_YOUTUBE_URL_RE = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+",
    re.IGNORECASE,
)


def run_analysis(user, channel_url: str) -> Analysis:
    """Validate the request, create an Analysis record, and dispatch the async task.

    Returns the Analysis immediately with status=PENDING so the caller can
    respond with 202 Accepted and the ID to poll.
    """
    _validate_url(channel_url)
    _check_quota(user)

    analysis = Analysis.objects.create(
        user=user,
        input_url=channel_url,
        status=StatusChoices.PENDING,
    )

    # Import here to avoid circular imports at module load time
    from apps.analysis.tasks import run_analysis_task
    run_analysis_task.delay(str(analysis.id))

    return analysis


def _validate_url(channel_url: str) -> None:
    if not _YOUTUBE_URL_RE.match(channel_url):
        raise ValidationError({"channel_url": "Must be a valid YouTube channel or video URL."})


def _check_quota(user) -> None:
    try:
        usage = user.usage_limit
    except Exception:
        # usage_limit doesn't exist yet — signal may not have run (e.g. fixture user)
        return

    if usage.video_analyzed >= usage.video_limit:
        raise QuotaExceededError()
