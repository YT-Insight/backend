from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import RegisterSerializer, UserProfileSerializer, ChangePasswordSerializer
from apps.subscriptions.models import Subscription, UsageLimit
from apps.subscriptions.serializer import SubscriptionSerializer, UsageLimitSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: inline_serializer("RegisterResponse", {"detail": serializers.CharField()})},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Account created successfully."}, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: inline_serializer("MeResponse", {
            "user": UserProfileSerializer(),
            "subscription": SubscriptionSerializer(),
            "usage": UsageLimitSerializer(),
        })},
    )
    def get(self, request):
        user = request.user
        now = timezone.now()
        next_month = now.replace(
            year=now.year + 1 if now.month == 12 else now.year,
            month=1 if now.month == 12 else now.month + 1,
            day=1, hour=0, minute=0, second=0, microsecond=0,
        )
        subscription, _ = Subscription.objects.get_or_create(user=user)
        usage, _ = UsageLimit.objects.get_or_create(
            user=user,
            defaults={
                "video_limit": settings.PLAN_VIDEO_LIMITS["free"],
                "reset_at": next_month,
            },
        )

        return Response({
            "user": UserProfileSerializer(user).data,
            "subscription": SubscriptionSerializer(subscription).data,
            "usage": UsageLimitSerializer(usage).data,
        })

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: inline_serializer("ChangePasswordResponse", {"detail": serializers.CharField()})},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password updated successfully."})


class LogoutView(APIView):
    """Blacklist the submitted refresh token so it can no longer be used."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer("LogoutRequest", {"refresh": serializers.CharField()}),
        responses={204: None},
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            # Already blacklisted or invalid — treat as successful logout
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
