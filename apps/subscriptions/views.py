from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import SubscriptionSerializer, UsageLimitSerializer, PlanTierSerializer
from .services.stripe_service import (
    create_checkout_session,
    create_billing_portal,
    handle_webhook_event,
)


class PlansView(APIView):
    """Public endpoint — returns plan tiers with pricing and features."""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses={200: PlanTierSerializer(many=True)})
    def get(self, request):
        serializer = PlanTierSerializer(settings.PLAN_METADATA, many=True)
        return Response(serializer.data)


class SubscriptionMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: inline_serializer("SubscriptionMeResponse", {
            "subscription": SubscriptionSerializer(),
            "usage": UsageLimitSerializer(),
        })},
    )
    def get(self, request):
        return Response({
            "subscription": SubscriptionSerializer(request.user.subscription).data,
            "usage": UsageLimitSerializer(request.user.usage_limit).data,
        })


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer("CheckoutRequest", {
            "plan": serializers.ChoiceField(choices=["basic", "pro"]),
        }),
        responses={200: inline_serializer("CheckoutResponse", {"checkout_url": serializers.URLField()})},
    )
    def post(self, request):
        plan = request.data.get("plan", "")

        if plan not in ("basic", "pro"):
            return Response(
                {"detail": "plan must be 'basic' or 'pro'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        checkout_url = create_checkout_session(request.user, plan)
        return Response({"checkout_url": checkout_url})


class BillingPortalView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: inline_serializer("BillingPortalResponse", {"portal_url": serializers.URLField()})},
    )
    def post(self, request):
        try:
            portal_url = create_billing_portal(request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"portal_url": portal_url})


class StripeWebhookView(APIView):
    """Stripe calls this endpoint — no JWT auth, verified by signature instead."""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(exclude=True)
    def post(self, request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            handle_webhook_event(request.body, sig_header)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "ok"})
