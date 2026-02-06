from django.urls import path
from .views import RegisterAPIView, MeAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("me/", MeAPIView.as_view(), name="me")
]