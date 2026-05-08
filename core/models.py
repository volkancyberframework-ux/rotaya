# core/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from PIL import Image, ImageOps

from django.db import models

import random
import string
from django.db import models


class PaymentSetting(models.Model):
    bank_name = models.CharField(max_length=120, default="Banka adı")
    account_holder = models.CharField(max_length=150, default="Volkan Güler")
    iban = models.CharField(max_length=50)
    youtube_join_url = models.URLField(
        default="https://www.youtube.com/channel/UCki5h5npPunCWXENktDcNBA/join"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_holder}"


class BankTransferOrder(models.Model):
    PLAN_CHOICES = (
        ("basic", "Rotaya Basic"),
        ("premium", "Rotaya Premium"),
    )

    email = models.EmailField()
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_code = models.CharField(max_length=8, unique=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.payment_code:
            self.payment_code = self.generate_payment_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_payment_code():
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not BankTransferOrder.objects.filter(payment_code=code).exists():
                return code

    def __str__(self):
        return f"{self.email} - {self.plan} - {self.payment_code}"


class RegistrationCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    valid_date = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.valid_date}"


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories"
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Sub Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Mentor(models.Model):
    ANONYMOUS_IMAGE_CHOICES = [
        ("anonymous/blur-1.jpg", "Anonim Görsel 1"),
        ("anonymous/blur-2.jpg", "Anonim Görsel 2"),
        ("anonymous/blur-3.jpg", "Anonim Görsel 3"),
        ("anonymous/blur-4.jpg", "Anonim Görsel 4"),
        ("anonymous/blur-5.jpg", "Anonim Görsel 5"),
        ("anonymous/blur-6.jpg", "Anonim Görsel 6"),
        ("anonymous/blur-7.jpg", "Anonim Görsel 7"),
        ("anonymous/blur-8.jpg", "Anonim Görsel 8"),
        ("anonymous/blur-9.jpg", "Anonim Görsel 9"),
        ("anonymous/blur-10.jpg", "Anonim Görsel 10"),
    ]

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    title = models.CharField(max_length=160, blank=True, null=True)
    company = models.CharField(max_length=160, blank=True, null=True)
    location = models.CharField(max_length=160, blank=True, null=True)

    bio = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=500, blank=True, null=True)

    photo = models.ImageField(upload_to="mentors/", blank=True, null=True)

    # Eski blur_photo yerine bunu kullan
    use_anonymous_photo = models.BooleanField(default=False)
    anonymous_photo = models.CharField(
        max_length=100,
        choices=ANONYMOUS_IMAGE_CHOICES,
        default="anonymous/blur-1.jpg"
    )

    anonymize_name = models.BooleanField(default=False)
    show_on_homepage = models.BooleanField(default=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    review_count = models.PositiveIntegerField(default=0)
    mentee_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_quick_responder = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        if self.anonymize_name:
            return f"{self.first_name[0]}xxxx {self.last_name[0]}xxxx"
        return f"{self.first_name} {self.last_name}"

    @property
    def display_photo(self):
        if self.use_anonymous_photo:
            return self.anonymous_photo
        if self.photo:
            return self.photo.url
        return "assets/images/mentor/mentor-img-1.jpg"

    def __str__(self):
        return self.full_name

class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Başlangıç"),
        ("intermediate", "Orta"),
        ("advanced", "İleri"),
    ]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)

    subtitle = models.CharField(max_length=260, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    what_you_will_learn = models.TextField(
        blank=True,
        null=True,
        help_text="Her maddeyi yeni satıra yaz."
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses"
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses"
    )

    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses"
    )

    thumbnail = models.ImageField(upload_to="courses/thumbnails/", blank=True, null=True)

    duration_hours = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.50)
    rating_count = models.PositiveIntegerField(default=0)

    content_count = models.PositiveIntegerField(default=0)
    student_count = models.PositiveIntegerField(default=0)

    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    attachment = models.FileField(
    upload_to="courses/attachments/",
    blank=True,
    null=True
    )

    @property
    def duration_label(self):
        return f"{self.duration_hours}h {self.duration_minutes}m"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.thumbnail:
            img_path = self.thumbnail.path

            img = Image.open(img_path)
            img = ImageOps.exif_transpose(img)

            target_size = (800, 500)  # course için biraz daha geniş

            img = ImageOps.fit(
                img,
                target_size,
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.4)
            )

            img.save(img_path, quality=90)

    def __str__(self):
        return self.title


class CourseVideo(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="videos"
    )
    title = models.CharField(max_length=220)
    description = models.TextField(blank=True, null=True)

    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to="courses/videos/", blank=True, null=True)

    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=1)

    is_preview = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Plan(models.Model):
    PLAN_TYPE_CHOICES = [
        ("monthly", "Aylık"),
        ("premium", "Premium"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    plan_type = models.CharField(max_length=30, choices=PLAN_TYPE_CHOICES)
    price_usd = models.DecimalField(max_digits=8, decimal_places=2)

    description = models.TextField(blank=True, null=True)

    stripe_price_id = models.CharField(max_length=200, blank=True, null=True)
    lemonsqueezy_variant_id = models.CharField(max_length=200, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ${self.price_usd}"


class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile"
    )

    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers"
    )

    has_paid = models.BooleanField(default=False)
    is_active_member = models.BooleanField(default=False)

    stripe_customer_id = models.CharField(max_length=200, blank=True, null=True)
    lemonsqueezy_customer_id = models.CharField(max_length=200, blank=True, null=True)

    membership_started_at = models.DateTimeField(blank=True, null=True)
    membership_expires_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    registration_code = models.ForeignKey(
        RegistrationCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers"
    )

    def can_access_console(self):
        return self.has_paid and self.is_active_member

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    PAYMENT_PROVIDER_CHOICES = [
        ("stripe", "Stripe"),
        ("lemonsqueezy", "LemonSqueezy"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    provider = models.CharField(max_length=30, choices=PAYMENT_PROVIDER_CHOICES)
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default="pending")

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")

    provider_payment_id = models.CharField(max_length=250, blank=True, null=True)
    provider_checkout_id = models.CharField(max_length=250, blank=True, null=True)

    raw_payload = models.JSONField(blank=True, null=True)

    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.provider} - {self.status}"


class CourseReview(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="course_reviews"
    )

    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()

    is_approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "customer")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.course.title} - {self.rating}"


class SearchLog(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    result_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.query} - {self.result_count} results"

from django.db import models
from django.utils.text import slugify


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ("basari-hikayesi", "Başarı Hikayesi"),
        ("kariyer", "Kariyer"),
        ("topluluk", "Topluluk"),
        ("duyuru", "Duyuru"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="basari-hikayesi")
    excerpt = models.TextField(max_length=300, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="blog/", blank=True, null=True)

    author = models.ForeignKey(
        Mentor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts"
    )

    read_time = models.PositiveIntegerField(default=5)
    is_published = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def author_name(self):
        if self.author:
            return self.author.full_name
        return "Rotaya"

    @property
    def author_avatar_url(self):
        if self.author:
            if self.author.use_anonymous_photo:
                return self.author.anonymous_photo

            if self.author.photo:
                return self.author.photo.url

        return "assets/images/instructor/instructor-img-1.jpg"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

from django.utils import timezone
from datetime import timedelta


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ip_address} - blocked"


class RegistrationAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.is_successful}"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.is_successful}"


class LockedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lock_status")
    locked_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - locked"
