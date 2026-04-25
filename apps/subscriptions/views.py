from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import SubscriptionSerializer, UsageLimitSerializer
from .services.stripe_service import (
    create_checkout_session,
    create_billing_portal,
    handle_webhook_event,
)


class SubscriptionMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "subscription": SubscriptionSerializer(request.user.subscription).data,
            "usage": UsageLimitSerializer(request.user.usage_limit).data,
        })


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

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

    def post(self, request):
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            handle_webhook_event(request.body, sig_header)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "ok"})
