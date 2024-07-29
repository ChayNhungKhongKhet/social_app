import logging

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
import requests
import json
from urllib.parse import urlencode

from .forms import CustomUserCreationForm, LoginForm, CustomPasswordResetForm
from .common.common import is_htmx

# Create your views here.

logger = logging.getLogger("users")
User = get_user_model()


class GoogleLoginView(View):
    def get(self, request):
        google_auth_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email",
        }
        url = f"{google_auth_url}?{urlencode(params)}"
        return HttpResponseRedirect(url)


class GoogleOAuth2CallbackView(View):
    def get(self, request):
        code = request.GET.get("code")
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        user_info_response = requests.get(
            user_info_url, params={"access_token": access_token}
        )
        user_info = user_info_response.json()

        email = user_info.get("email")
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.save()

        login(request, user)
        return HttpResponseRedirect(reverse_lazy("index"))


class LoginView(View):
    template_name = "users/login/login.html"
    success_url = reverse_lazy("index")

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        _is_htmx = is_htmx(request)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if _is_htmx:
                    response = HttpResponse()
                    response["HX-Redirect"] = self.success_url
                    return response
                return HttpResponseRedirect(self.success_url)
            else:
                context = {
                    "form": form,
                    "errors": "Wrong email or password",
                }
                if _is_htmx:
                    status = 400
                    return JsonResponse(
                        {
                            "html": render_to_string(
                                "users/login/_form.html", context, self.request
                            )
                        },
                        status=status,
                    )
                return render(request, self.template_name, context)
        else:
            context = {"form": form, "errors": "Form is not valid"}
            if _is_htmx:
                status = 400
                return JsonResponse(
                    {
                        "html": render_to_string(
                            "users/login/_form.html", context, self.request
                        )
                    },
                    status=status,
                )
            return render(request, self.template_name, context, status=status)


class RegisterView(CreateView):
    template_name = "users/registration/register.html"
    form_class = CustomUserCreationForm

    def form_invalid(self, form):
        response = super().form_invalid(form)
        status = 400
        if is_htmx(self.request):
            context = {"form": form}
            return JsonResponse(
                {
                    "html": render_to_string(
                        "users/registration/register_form.html", context, self.request
                    )
                },
                status=status,
            )
        else:
            response.status_code = status
            return response

    def form_valid(self, form):
        form.save()
        return render(
            self.request, "users/registration/register_success.html", status=201
        )


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "users/reset_password/password_reset_email.html"
    subject_template_name = "users/reset_password/password_reset_subject.txt"
    template_name = "users/reset_password/password_reset.html"
    success_url = reverse_lazy("users:password_reset_done")
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        response = super().form_valid(form)

        logger.info(f"Attempting to send password reset email to: {email}")
        if is_htmx(self.request):
            response = HttpResponse()
            response["HX-Redirect"] = self.success_url
            return response
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        status = 400
        if is_htmx(self.request):
            context = {"form": form}
            html = render_to_string(
                "users/reset_password/password_reset_form.html",
                context,
                request=self.request,
            )
            return JsonResponse({"html": html}, status=status)
        else:
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_name"] = get_current_site(self.request).name
        context["domain"] = get_current_site(self.request).domain
        return context
