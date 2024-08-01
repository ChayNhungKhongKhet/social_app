import logging
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import PasswordResetView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View

from profiles.models import Profile
from profiles.forms import ProfileCreateForm
from .forms import CustomUserCreationForm, LoginForm, CustomPasswordResetForm
from .common.common import is_htmx

logger = logging.getLogger("users")
User = get_user_model()


class GoogleLoginView(View):
    google_auth_url = "https://accounts.google.com/o/oauth2/auth"
    google_scope = "openid profile email "

    def get(self, request):
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": self.google_scope,
        }
        url = f"{self.google_auth_url}?{urlencode(params)}"
        return HttpResponseRedirect(url)


class GoogleOAuth2CallbackView(View):
    token_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    def get(self, request):
        code = request.GET.get("code")
        token_data = self._get_token_data(code)
        token_response = requests.post(self.token_url, data=token_data)
        token_json = token_response.json()
        access_token = token_json.get("access_token")

        user_info_response = requests.get(
            self.user_info_url, params={"access_token": access_token}
        )
        user_info = user_info_response.json()


        user, created = self._get_or_create_user(user_info.get("email"))
        if created:
            self._create_profile(
                user,
                user_info.get("given_name"),
                user_info.get("family_name"),
                user_info.get("picture"),
            )
        login(request, user)
        return HttpResponseRedirect(reverse_lazy("index"))

    def _create_profile(
        self,
        user,
        first_name,
        last_name,
        avatar,
    ):
        profile = Profile.objects.create(user=user)
        profile.first_name = first_name
        profile.last_name = last_name
        profile.avatar = avatar
        profile.save()

    def _get_token_data(self, code):
        return {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

    def _get_or_create_user(self, email):
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.save()
        return user, created


class LoginView(View):
    template_name = "users/login/login.html"
    success_url = reverse_lazy("index")

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = self._authenticate_user(request, form)
            if user:
                login(request, user)
                return self._handle_htmx_redirect()
            else:
                return self._render_form_with_errors(form, "Wrong email or password")
        else:
            return self._render_form_with_errors(form, "Form is not valid")

    def _authenticate_user(self, request, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        return authenticate(request, email=email, password=password)

    def _handle_htmx_redirect(self):
        if is_htmx(self.request):
            response = HttpResponse()
            response["HX-Redirect"] = self.success_url
            return response
        return HttpResponseRedirect(self.success_url)

    def _render_form_with_errors(self, form, error_message):
        context = {"form": form, "errors": error_message}
        if is_htmx(self.request):
            html = render_to_string("users/login/_form.html", context, self.request)
            return JsonResponse({"html": html}, status=400)
        return render(self.request, self.template_name, context)


class RegisterView(View):
    template_name = "users/registration/register.html"

    def get(self, request):

        context = self._get_forms_context()
        return render(request, self.template_name, context)

    def post(self, request):
        user_form, profile_form = self._get_forms_from_post(request)
        if user_form.is_valid() and profile_form.is_valid():
            self._save_user_and_profile(user_form, profile_form)
            return render(request, "users/registration/register_success.html")
        return self._handle_invalid_forms(user_form, profile_form)

    def _get_forms_context(self):
        user_form = CustomUserCreationForm(prefix="user_form")
        profile_form = ProfileCreateForm(prefix="profile_form")
        return {"user_form": user_form, "profile_form": profile_form}

    def _get_forms_from_post(self, request):
        user_form = CustomUserCreationForm(request.POST, prefix="user_form")
        profile_form = ProfileCreateForm(request.POST, prefix="profile_form")
        return user_form, profile_form

    def _save_user_and_profile(self, user_form, profile_form):
        user = user_form.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()

    def _handle_invalid_forms(self, user_form, profile_form):
        context = {"user_form": user_form, "profile_form": profile_form}
        if is_htmx(self.request):
            html = render_to_string(
                "users/registration/register_form.html", context, self.request
            )
            return JsonResponse({"html": html}, status=400)
        return render(
            self.request,
            self.template_name,
            context,
        )


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "users/reset_password/password_reset_email.html"
    subject_template_name = "users/reset_password/password_reset_subject.txt"
    template_name = "users/reset_password/password_reset.html"
    success_url = reverse_lazy("users:password_reset_done")
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        logger.info(f"Attempting to send password reset email to: {email}")
        response = super().form_valid(form)
        if is_htmx(self.request):
            response = HttpResponse()
            response["HX-Redirect"] = self.success_url
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if is_htmx(self.request):
            context = {"form": form}
            html = render_to_string(
                "users/reset_password/password_reset_form.html", context, self.request
            )
            return JsonResponse({"html": html}, status=400)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = get_current_site(self.request).name
        context["domain"] = get_current_site(self.request).domain
        return context
