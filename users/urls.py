from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from .views import LoginView, RegisterView, CustomPasswordResetView, GoogleLoginView, GoogleOAuth2CallbackView


app_name = "users"
urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path('login/google/', GoogleLoginView.as_view(), name='google_login'),
    path('oauth2callback/', GoogleOAuth2CallbackView.as_view(), name='oauth2callback'),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("register", RegisterView.as_view(), name="register"),
    path(
        "password_reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/reset_password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/reset_password/password_reset_confirm.html",
            success_url = reverse_lazy("users:password_reset_complete")
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/reset_password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
