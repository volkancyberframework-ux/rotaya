from datetime import timedelta

from django.conf import settings
from django.contrib.auth.signals import user_login_failed, user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from .models import LoginAttempt, BlockedIP


def get_client_ip(request):
    if not request:
        return None

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def is_admin_login_request(request):
    if not request:
        return False

    admin_path = getattr(settings, "ADMIN_PROTECTED_PATH", "/admin/")
    return request.path.startswith(admin_path)


@receiver(user_login_failed)
def track_failed_admin_login(sender, credentials, request, **kwargs):
    if not is_admin_login_request(request):
        return

    ip_address = get_client_ip(request)
    username = credentials.get("username", "")

    LoginAttempt.objects.create(
        username=username,
        ip_address=ip_address,
        is_successful=False,
    )

    max_attempts = getattr(settings, "ADMIN_MAX_FAILED_LOGIN_ATTEMPTS", 5)
    block_minutes = getattr(settings, "ADMIN_LOGIN_BLOCK_MINUTES", 30)

    since = timezone.now() - timedelta(minutes=block_minutes)

    failed_count = LoginAttempt.objects.filter(
        ip_address=ip_address,
        is_successful=False,
        created_at__gte=since,
    ).count()

    if failed_count >= max_attempts:
        BlockedIP.objects.update_or_create(
            ip_address=ip_address,
            defaults={
                "reason": f"Admin login failed {failed_count} times",
                "is_active": True,
            }
        )


@receiver(user_logged_in)
def track_successful_admin_login(sender, request, user, **kwargs):
    if not is_admin_login_request(request):
        return

    ip_address = get_client_ip(request)

    LoginAttempt.objects.create(
        username=user.username,
        ip_address=ip_address,
        is_successful=True,
    )

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BankTransferOrder, Customer
from .utils import send_telegram_message


@receiver(post_save, sender=BankTransferOrder)
def notify_bank_transfer_order(sender, instance, created, **kwargs):
    if created:
        send_telegram_message(
            f"""
💸 Yeni Bank Transfer Order

📧 Email: {instance.email}
📦 Plan: {instance.plan}
💰 Tutar: {instance.discounted_price}
🔑 Kod: {instance.payment_code}
"""
        )


@receiver(post_save, sender=Customer)
def notify_new_customer(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        send_telegram_message(
            f"""
🎉 Yeni Kullanıcı Kaydı

👤 Username: {user.username}
📧 Email: {user.email}
💳 Paid: {instance.has_paid}
✅ Active: {instance.is_active_member}
"""
        )
