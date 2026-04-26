from rest_framework.permissions import BasePermission
from apps.common.exceptions import QuotaExceededError


class HasAnalysisQuota(BasePermission):
    """Deny the request when the user has exhausted their monthly analysis limit."""

    def has_permission(self, request, view):
        try:
            usage = request.user.usage_limit
        except Exception:
            # No usage record yet — allow and let the signal create it
            return True

        if usage.video_analyzed >= usage.video_limit:
            raise QuotaExceededError()

        return True
