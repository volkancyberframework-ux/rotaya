from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve

from core.views import (
    home,
    courses,
    course_detail,
    mentor,
    signup,
    login_view,
    logout_view,
    create_bank_transfer_order,
    blog,
    blog_detail,
)


urlpatterns = [
    path("rotaya-control-panel-92x7/", admin.site.urls),

    path("", home, name="home"),
    path("courses/", courses, name="courses"),
    path("course/<slug:slug>/", course_detail, name="course_detail"),
    path("mentor/", mentor, name="mentor"),

    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path(
        "create-bank-transfer-order/",
        create_bank_transfer_order,
        name="create_bank_transfer_order",
    ),

    path("blog/", blog, name="blog"),
    path("blog/<slug:slug>/", blog_detail, name="blog_detail"),
]


# Render Disk media files
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
