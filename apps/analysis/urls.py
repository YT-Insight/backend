from django.urls import path
from .views import AnalysisCreateView, AnalysisListView, AnalysisDetailView, AnalysisStatusView

urlpatterns = [
    path("", AnalysisListView.as_view(), name="analysis-list"),
    path("create/", AnalysisCreateView.as_view(), name="analysis-create"),
    path("<uuid:pk>/", AnalysisDetailView.as_view(), name="analysis-detail"),
    path("<uuid:pk>/status/", AnalysisStatusView.as_view(), name="analysis-status"),
]
