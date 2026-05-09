from random import sample
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import (
    Course,
    Mentor,
    CourseReview,
    Category,
    SubCategory,
    SearchLog,
    Customer,
)
from django.contrib import messages
from django.utils import timezone

from .models import Customer, RegistrationCode
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import CourseReview
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import (
    RegistrationAttempt,
    LoginAttempt,
    BlockedIP,
    LockedUser,
)
from core.utils import send_telegram_message

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import BankTransferOrder


@require_POST
def create_bank_transfer_order(request):
    email = request.POST.get("email")
    plan = request.POST.get("plan")
    price = request.POST.get("price")

    if not email or not plan or not price:
        return JsonResponse({
            "success": False,
            "message": "E-posta, plan ve fiyat zorunludur."
        }, status=400)

    try:
        original_price = Decimal(price)
    except:
        return JsonResponse({
            "success": False,
            "message": "Geçersiz fiyat."
        }, status=400)

    discounted_price = original_price * Decimal("0.80")

    order = BankTransferOrder.objects.create(
        email=email,
        plan=plan,
        original_price=original_price,
        discounted_price=discounted_price
    )

    send_telegram_message(
        f"""
    💸 Yeni Bank Transfer Order

    📧 Email: {order.email}
    📦 Plan: {order.plan}
    💰 Tutar: {order.discounted_price}
    🔑 Kod: {order.payment_code}
    """
    )

    return JsonResponse({
        "success": True,
        "email": order.email,
        "payment_code": order.payment_code,
        "discounted_price": str(order.discounted_price),
    })

def user_has_access(request):
    return (
        request.user.is_authenticated
        and hasattr(request.user, "customer_profile")
        and request.user.customer_profile.has_paid
        and request.user.customer_profile.is_active_member
    )


def home(request):
    courses = (
        Course.objects
        .filter(is_published=True)
        .select_related("mentor", "category", "subcategory")
        .order_by("?")[:10]
    )

    if user_has_access(request):
        mentors = (
            Mentor.objects
            .filter(is_active=True)
            .order_by("?")[:4]
        )
    else:
        mentors = (
            Mentor.objects
            .filter(is_active=True, show_on_homepage=True)
            .order_by("?")[:4]
        )

    course_reviews = (
        CourseReview.objects
        .filter(is_approved=True)
        .select_related("customer", "customer__user")
        .order_by("?")[:3]
    )

    categories = list(Category.objects.all())
    subcategories = list(SubCategory.objects.all())

    search_terms = categories + subcategories
    if len(search_terms) > 10:
        search_terms = sample(search_terms, 10)

    return render(request, "home.html", {
        "courses": courses,
        "mentors": mentors,
        "course_reviews": course_reviews,
        "search_terms": search_terms,
    })


def mentor(request):
    query = request.GET.get("q", "").strip()

    if user_has_access(request):
        mentors = (
            Mentor.objects
            .filter(is_active=True)
            .prefetch_related("courses")
            .order_by("-created_at")
        )
    else:
        mentors = (
            Mentor.objects
            .filter(is_active=True, show_on_homepage=True)
            .prefetch_related("courses")
            .order_by("-created_at")
        )

    if query:
        mentors = mentors.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query) |
            Q(bio__icontains=query) |
            Q(skills__icontains=query)
        )

    return render(request, "mentor.html", {
        "mentors": mentors,
        "query": query,
    })

def courses(request):
    q = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")
    subcategory_slug = request.GET.get("subcategory")
    level = request.GET.get("level")
    rating = request.GET.get("rating")
    sort = request.GET.get("sort")

    course_list = (
        Course.objects
        .filter(is_published=True)
        .select_related("mentor", "category", "subcategory")
    )

    selected_category = None
    selected_subcategory = None

    if q:
        course_list = course_list.filter(
            Q(title__icontains=q) |
            Q(subtitle__icontains=q) |
            Q(short_description__icontains=q) |
            Q(description__icontains=q) |
            Q(what_you_will_learn__icontains=q) |
            Q(category__name__icontains=q) |
            Q(subcategory__name__icontains=q) |
            Q(mentor__title__icontains=q) |
            Q(mentor__company__icontains=q) |
            Q(mentor__location__icontains=q) |
            Q(mentor__bio__icontains=q) |
            Q(mentor__skills__icontains=q)
        )

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        course_list = course_list.filter(category=selected_category)

    if subcategory_slug:
        selected_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        course_list = course_list.filter(subcategory=selected_subcategory)

    if level:
        course_list = course_list.filter(level=level)

    if rating:
        course_list = course_list.filter(rating__gte=rating)

    if sort == "popular":
        course_list = course_list.order_by("-student_count")
    elif sort == "rating":
        course_list = course_list.order_by("-rating")
    else:
        course_list = course_list.order_by("-created_at")

    result_count = course_list.count()

    if q:
        SearchLog.objects.create(
            query=q,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            result_count=result_count,
        )

    categories = Category.objects.all().order_by("name")
    subcategories = SubCategory.objects.all().order_by("name")

    return render(request, "courses.html", {
        "courses": course_list,
        "categories": categories,
        "subcategories": subcategories,
        "selected_category": selected_category,
        "selected_subcategory": selected_subcategory,
        "q": q,
        "query": q,
        "level": level,
        "rating": rating,
        "sort": sort,
        "result_count": result_count,
    })


@login_required(login_url="/login/")
def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.select_related("mentor", "category", "subcategory"),
        slug=slug,
        is_published=True
    )

    if request.method == "POST":
        if request.user.is_authenticated:
            rating = request.POST.get("rating")
            comment = request.POST.get("comment")

            customer = request.user.customer_profile

            CourseReview.objects.create(
                course=course,
                customer=customer,
                rating=rating,
                comment=comment,
                is_approved=False
            )

            messages.success(request, "Yorumun onaya gönderildi.")
            return redirect("course_detail", slug=course.slug)

        messages.error(request, "Yorum yazmak için giriş yapmalısın.")
        return redirect("course_detail", slug=course.slug)

    videos = course.videos.filter(is_published=True).order_by("order")
    first_video = videos.first()

    reviews = course.reviews.filter(is_approved=True).select_related(
        "customer",
        "customer__user"
    )[:10]

    learning_items = []
    if course.what_you_will_learn:
        learning_items = [
            item.strip()
            for item in course.what_you_will_learn.splitlines()
            if item.strip()
        ]

    return render(request, "course_detail.html", {
        "course": course,
        "videos": videos,
        "first_video": first_video,
        "reviews": reviews,
        "learning_items": learning_items,
    })
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next") or "/"
        ip = get_client_ip(request)

        user_obj = User.objects.filter(username=username).first()

        if user_obj and LockedUser.objects.filter(user=user_obj, is_active=True).exists():
            messages.error(request, "Bu kullanıcı çok fazla hatalı giriş nedeniyle kilitlendi.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        user = authenticate(request, username=username, password=password)

        if user is not None:
            LoginAttempt.objects.create(
                username=username,
                ip_address=ip,
                is_successful=True
            )

            login(request, user)
            return redirect(next_url)

        LoginAttempt.objects.create(
            username=username,
            ip_address=ip,
            is_successful=False
        )

        failed_login_count = LoginAttempt.objects.filter(
            username=username,
            is_successful=False
        ).count()

        if user_obj and failed_login_count >= 10:
            LockedUser.objects.get_or_create(
                user=user_obj,
                defaults={"reason": "10'dan fazla hatalı parola denemesi"}
            )

        messages.error(request, "Kullanıcı adı veya şifre hatalı.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    return redirect("/")
def logout_view(request):
    logout(request)
    return redirect("/")


def signup(request):
    if request.method == "POST":
        ip = get_client_ip(request)

        failed_count = RegistrationAttempt.objects.filter(
            ip_address=ip,
            is_successful=False
        ).count()

        if failed_count >= 10:
            BlockedIP.objects.get_or_create(
                ip_address=ip,
                defaults={"reason": "10'dan fazla başarısız kayıt denemesi"}
            )
            messages.error(request, "Çok fazla başarısız kayıt denemesi yapıldı.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        registration_code_value = request.POST.get("registration_code", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        registration_code = RegistrationCode.objects.filter(
            code=registration_code_value,
            valid_date=timezone.localdate(),
            is_active=True
        ).first()

        if not registration_code:
            RegistrationAttempt.objects.create(ip_address=ip, is_successful=False)
            messages.error(request, "Doğrulama kodu hatalı veya bugün için geçerli değil.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if not username:
            RegistrationAttempt.objects.create(ip_address=ip, is_successful=False)
            messages.error(request, "YouTube kullanıcı adı zorunludur.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if User.objects.filter(username=username).exists():
            RegistrationAttempt.objects.create(ip_address=ip, is_successful=False)
            messages.error(request, "Bu kullanıcı adı zaten alınmış.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if password1 != password2:
            RegistrationAttempt.objects.create(ip_address=ip, is_successful=False)
            messages.error(request, "Şifreler eşleşmiyor.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if len(password1) < 8:
            RegistrationAttempt.objects.create(ip_address=ip, is_successful=False)
            messages.error(request, "Şifre en az 8 karakter olmalıdır.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        try:
            validate_password(password1)
        except ValidationError as e:
            RegistrationAttempt.objects.create(ip_address=ip, is_successful=False)
            messages.error(request, " ".join(e.messages))
            return redirect(request.META.get("HTTP_REFERER", "/"))

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        Customer.objects.create(
            user=user,
            has_paid=True,
            is_active_member=True,
            membership_started_at=timezone.now(),
            registration_code=registration_code,
        )

        send_telegram_message(
        f"""
        🎉 Yeni Kullanıcı Kaydı

        👤 Username: {username}
        📧 Email: {email}
        🌍 IP: {ip}
        """
        )

        RegistrationAttempt.objects.create(ip_address=ip, is_successful=True)

        login(request, user)
        return redirect("/?login=success")

    return redirect("/")
from django.shortcuts import render, get_object_or_404
from .models import BlogPost


def blog(request):
    blog_posts = BlogPost.objects.filter(is_published=True)

    return render(request, "blog.html", {
        "blog_posts": blog_posts
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    return render(request, "blog_detail.html", {
        "post": post
    })
