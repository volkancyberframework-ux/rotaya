from django.contrib import admin

from .models import (
    Category,
    SubCategory,
    Mentor,
    Course,
    CourseVideo,
    Plan,
    Customer,
    Payment,
    CourseReview,
    SearchLog,
    RegistrationCode,
    PaymentSetting,
    BankTransferOrder,
    BlogPost,
    BlockedIP,
    RegistrationAttempt,
    LoginAttempt,
    LockedUser,
)


admin.site.site_header = "Rotaya Yönetim Paneli"
admin.site.site_title = "Rotaya Admin"
admin.site.index_title = "Rotaya Yönetim Alanı"


# =========================
# İÇERİK YÖNETİMİ
# =========================

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Mentor)
admin.site.register(Course)
admin.site.register(CourseVideo)
admin.site.register(CourseReview)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author_name", "is_published", "created_at")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "excerpt", "content", "author_name")
    prepopulated_fields = {"slug": ("title",)}


# =========================
# ÜYELİK / MÜŞTERİ YÖNETİMİ
# =========================

admin.site.register(Plan)
admin.site.register(Customer)


@admin.register(RegistrationCode)
class RegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "valid_date", "last_day", "is_active", "created_at")
    search_fields = ("code",)
    list_filter = ("is_active", "valid_date", "last_day")

# =========================
# ÖDEME YÖNETİMİ
# =========================

admin.site.register(Payment)


@admin.register(PaymentSetting)
class PaymentSettingAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "account_holder", "iban", "is_active")
    list_filter = ("is_active",)
    search_fields = ("bank_name", "account_holder", "iban")


@admin.register(BankTransferOrder)
class BankTransferOrderAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "plan",
        "original_price",
        "discounted_price",
        "payment_code",
        "is_paid",
        "created_at",
    )
    list_filter = ("plan", "is_paid", "created_at")
    search_fields = ("email", "payment_code")


# =========================
# ARAMA / LOG YÖNETİMİ
# =========================

@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("query", "user", "result_count", "ip_address", "created_at")
    search_fields = ("query", "ip_address", "user_agent")
    list_filter = ("created_at",)


# =========================
# GÜVENLİK YÖNETİMİ
# =========================

@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "reason", "blocked_at", "is_active")
    list_filter = ("is_active", "blocked_at")
    search_fields = ("ip_address", "reason")
    ordering = ("-blocked_at",)


@admin.register(RegistrationAttempt)
class RegistrationAttemptAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "is_successful", "created_at")
    list_filter = ("is_successful", "created_at")
    search_fields = ("ip_address",)
    ordering = ("-created_at",)


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("username", "ip_address", "is_successful", "created_at")
    list_filter = ("is_successful", "created_at")
    search_fields = ("username", "ip_address")
    ordering = ("-created_at",)


@admin.register(LockedUser)
class LockedUserAdmin(admin.ModelAdmin):
    list_display = ("user", "reason", "locked_at", "is_active")
    list_filter = ("is_active", "locked_at")
    search_fields = ("user__username", "reason")
    ordering = ("-locked_at",)
