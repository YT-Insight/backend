from django.urls import path
from .views import SubscriptionMeView, CheckoutView, BillingPortalView, StripeWebhookView

urlpatterns = [
    path("me/", SubscriptionMeView.as_view(), name="subscription-me"),
    path("checkout/", CheckoutView.as_view(), name="subscription-checkout"),
    path("portal/", BillingPortalView.as_view(), name="subscription-portal"),
    path("webhook/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
