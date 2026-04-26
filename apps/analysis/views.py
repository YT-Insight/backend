from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.analysis.models import Analysis
from apps.analysis.permissions import HasAnalysisQuota
from apps.analysis.serializer import (
    AnalysisInputSerializer,
    AnalysisListSerializer,
    AnalysisDetailSerializer,
    AnalysisStatusSerializer,
)
from apps.analysis.services.analysis_service import run_analysis
from apps.common.pagination import StandardPagination


class AnalysisThrottle(UserRateThrottle):
    scope = "analysis"


class AnalysisCreateView(APIView):
    permission_classes = [IsAuthenticated, HasAnalysisQuota]
    throttle_classes = [AnalysisThrottle]

    @extend_schema(request=AnalysisInputSerializer, responses={202: AnalysisStatusSerializer})
    def post(self, request):
        serializer = AnalysisInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        analysis = run_analysis(
            user=request.user,
            channel_url=serializer.validated_data["channel_url"],
        )

        return Response(
            AnalysisStatusSerializer(analysis).data,
            status=status.HTTP_202_ACCEPTED,
        )


class AnalysisListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            Analysis.objects.filter(user=self.request.user)
            .select_related("channel")
            .order_by("-created_at")
        )


class AnalysisDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisDetailSerializer

    def get_queryset(self):
        return (
            Analysis.objects.filter(user=self.request.user)
            .select_related("channel", "result")
            .prefetch_related("topics", "questions", "suggestions")
        )


class AnalysisStatusView(RetrieveAPIView):
    """Lightweight endpoint for frontend polling while analysis is in progress."""
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisStatusSerializer

    def get_queryset(self):
        return Analysis.objects.filter(user=self.request.user)
