from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone


def _first_of_next_month():
    now = timezone.now()
    year = now.year + 1 if now.month == 12 else now.year
    month = 1 if now.month == 12 else now.month + 1
    return now.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_resources(sender, instance, created, **kwargs):
    if not created:
        return

    from apps.subscriptions.models import Subscription, UsageLimit

    Subscription.objects.create(user=instance)
    UsageLimit.objects.create(
        user=instance,
        video_limit=settings.PLAN_VIDEO_LIMITS["free"],
        reset_at=_first_of_next_month(),
    )
