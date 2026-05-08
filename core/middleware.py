from django.http import HttpResponseForbidden
from .models import BlockedIP


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class BlockedIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)

        if ip and BlockedIP.objects.filter(ip_address=ip, is_active=True).exists():
            return HttpResponseForbidden("Bu IP adresinden erişim geçici olarak engellendi.")

        return self.get_response(request)


from datetime import timedelta

from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import BlockedIP


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


class AdminBlockedIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_path = getattr(settings, "ADMIN_PROTECTED_PATH", "/admin/")

        if request.path.startswith(admin_path):
            ip_address = get_client_ip(request)

            blocked_ip = BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).first()

            if blocked_ip:
                block_minutes = getattr(settings, "ADMIN_LOGIN_BLOCK_MINUTES", 30)
                unblock_time = blocked_ip.blocked_at + timedelta(minutes=block_minutes)

                if timezone.now() < unblock_time:
                    return HttpResponseForbidden(
                        "Too many failed login attempts. Please try again later."
                    )

                blocked_ip.is_active = False
                blocked_ip.save(update_fields=["is_active"])

        return self.get_response(request)
