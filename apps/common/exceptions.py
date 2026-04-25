from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


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


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Unhandled exception — return a clean 500 instead of letting Django crash
    return Response(
        {"detail": "An unexpected error occurred. Please try again."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
