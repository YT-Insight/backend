import logging
from datetime import datetime, timezone

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


def _stripe() -> stripe:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


# ── Public API ────────────────────────────────────────────────────────────────

def create_checkout_session(user, plan: str) -> str:
    """Create a Stripe Checkout session and return the URL to redirect the user to."""
    price_id = _price_id_for_plan(plan)

    session = _stripe().checkout.Session.create(
        customer_email=user.email,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.FRONTEND_URL}/billing?success=true",
        cancel_url=f"{settings.FRONTEND_URL}/billing?canceled=true",
        metadata={"user_id": str(user.id), "plan": plan},
    )
    return session.url


def create_billing_portal(user) -> str:
    """Create a Stripe Customer Portal session and return its URL."""
    sub = user.subscription

    if not sub.stripe_subscription_id:
        raise ValueError("No active Stripe subscription found for this account.")

    stripe_sub = _stripe().Subscription.retrieve(sub.stripe_subscription_id)
    customer_id = stripe_sub["customer"]

    portal = _stripe().billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.FRONTEND_URL}/billing",
    )
    return portal.url


def handle_webhook_event(payload: bytes, sig_header: str) -> None:
    """Verify the Stripe signature and dispatch to the appropriate handler."""
    try:
        event = _stripe().Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError as exc:
        raise ValueError("Stripe webhook signature verification failed.") from exc
    except ValueError as exc:
        raise ValueError(f"Invalid webhook payload: {exc}") from exc

    _HANDLERS = {
        "customer.subscription.created": _on_subscription_created,
        "customer.subscription.updated": _on_subscription_updated,
        "customer.subscription.deleted": _on_subscription_deleted,
        "invoice.payment_failed": _on_payment_failed,
    }

    handler = _HANDLERS.get(event["type"])
    if handler:
        handler(event["data"]["object"])
    else:
        logger.debug("Unhandled Stripe event type: %s", event["type"])


# ── Webhook handlers ──────────────────────────────────────────────────────────

def _on_subscription_created(stripe_sub: dict) -> None:
    _sync_subscription(stripe_sub)


def _on_subscription_updated(stripe_sub: dict) -> None:
    _sync_subscription(stripe_sub)


def _on_subscription_deleted(stripe_sub: dict) -> None:
    from apps.subscriptions.models import Subscription

    Subscription.objects.filter(
        stripe_subscription_id=stripe_sub["id"],
    ).update(
        plan="free",
        status="canceled",
        stripe_subscription_id=None,
        current_period_end=None,
    )
    logger.info("Subscription %s deleted — user downgraded to free.", stripe_sub["id"])


def _on_payment_failed(invoice: dict) -> None:
    from apps.subscriptions.models import Subscription

    stripe_sub_id = invoice.get("subscription")
    if stripe_sub_id:
        Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).update(
            status="past_due",
        )
        logger.warning("Payment failed for subscription %s.", stripe_sub_id)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _sync_subscription(stripe_sub: dict) -> None:
    """Update local Subscription and UsageLimit to match Stripe state."""
    from apps.subscriptions.models import Subscription

    metadata = stripe_sub.get("metadata", {})
    user_id = metadata.get("user_id")

    if not user_id:
        logger.warning("Stripe subscription %s has no user_id in metadata.", stripe_sub["id"])
        return

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("Stripe webhook references unknown user_id: %s", user_id)
        return

    plan = _plan_from_stripe(stripe_sub)
    raw_status = stripe_sub.get("status", "active")
    mapped_status = raw_status if raw_status in ("active", "canceled", "past_due") else "active"
    period_end_ts = stripe_sub.get("current_period_end")
    period_end = datetime.fromtimestamp(period_end_ts, tz=timezone.utc) if period_end_ts else None

    Subscription.objects.filter(user=user).update(
        stripe_subscription_id=stripe_sub["id"],
        plan=plan,
        status=mapped_status,
        current_period_end=period_end,
    )

    # Update the usage cap to match the new plan
    new_limit = settings.PLAN_VIDEO_LIMITS.get(plan, 5)
    user.usage_limit.video_limit = new_limit
    user.usage_limit.save(update_fields=["video_limit", "updated_at"])

    logger.info("Synced subscription for user %s → plan=%s status=%s", user_id, plan, mapped_status)


def _plan_from_stripe(stripe_sub: dict) -> str:
    items = stripe_sub.get("items", {}).get("data", [])
    if not items:
        return "free"

    price_id = items[0]["price"]["id"]
    if price_id == settings.STRIPE_BASIC_PRICE_ID:
        return "basic"
    if price_id == settings.STRIPE_PRO_PRICE_ID:
        return "pro"
    return "free"


def _price_id_for_plan(plan: str) -> str:
    mapping = {
        "basic": settings.STRIPE_BASIC_PRICE_ID,
        "pro": settings.STRIPE_PRO_PRICE_ID,
    }
    if plan not in mapping:
        raise ValueError(f"Unknown plan: {plan!r}. Must be 'basic' or 'pro'.")
    return mapping[plan]
