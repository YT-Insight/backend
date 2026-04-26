import logging

from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class QuotaExceededError(PermissionDenied):
    default_detail = "Monthly analysis limit reached. Upgrade your plan to continue."
    default_code = "quota_exceeded"


class YouTubeAPIError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Failed to fetch data from YouTube. Please try again."
    default_code = "youtube_api_error"


class AIServiceError(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "AI analysis service is temporarily unavailable."
    default_code = "ai_service_error"


class PipelineUnavailableError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Analysis pipeline is temporarily unavailable. Please try again in a moment."
    default_code = "pipeline_unavailable"


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    logger.exception("Unhandled exception in API view: %s", exc)
    return Response(
        {"detail": "An unexpected error occurred. Please try again."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
