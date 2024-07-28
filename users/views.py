import logging

from django.forms import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site

from .forms import CustomUserCreationForm, LoginForm, CustomPasswordResetForm
from .common.common import is_htmx

# Create your views here.

logger = logging.getLogger("users")


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
                        {"html": render_to_string("users/login/_form.html", context)},
                        status=status,
                    )
                return render(request, self.template_name, context, status=status)
        else:
            context = {"form": form, "errors": "Form is not valid"}
            if _is_htmx:
                status = 400
                return JsonResponse(
                    {"html": render_to_string("users/login/_form.html", context)},
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
                {"html": render_to_string("users/registration/register_form.html", context)},
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
