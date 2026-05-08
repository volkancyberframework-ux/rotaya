from .models import Category


def navbar_categories(request):
    categories = (
        Category.objects
        .prefetch_related("subcategories")
        .order_by("name")
    )

    return {
        "navbar_categories": categories
    }

from .models import PaymentSetting


def payment_settings(request):
    payment_setting = PaymentSetting.objects.filter(is_active=True).first()
    return {
        "payment_setting": payment_setting
    }
