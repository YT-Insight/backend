from django.urls import path
from .views import AnalysisCreateView

urlpatterns = [
    path("", AnalysisCreateView.as_view(), name="analysis-create")
]