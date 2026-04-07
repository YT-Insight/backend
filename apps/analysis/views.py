from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.analysis.serializer import AnalysisInputSerializer, AnalysisOutputSerializer
from apps.analysis.services.analysis_service import run_analysis

# Create your views here.

class AnalysisCreateView(APIView):
    permission_classes = IsAuthenticated

    def post(self, request):
        input_serializer = AnalysisInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = run_analysis(
            user=request.user,
            channel_url=input_serializer.validated_data["channel_url"]
        )

        output_serializer = AnalysisOutputSerializer(result)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)