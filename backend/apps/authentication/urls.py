from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("set-csrf-token/", views.set_csrf_token, name="set_csrf_token"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("user/timezone/", views.update_timezone, name="update_timezone"),
    path("user/profile/", views.update_profile, name="update_profile"),
    path("user/", views.user, name="user"),
    path("register/", views.register, name="register"),
]
