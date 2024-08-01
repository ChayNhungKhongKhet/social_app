from django.shortcuts import render
from django.views.generic import UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

from profiles.models import Profile
from profiles.forms import ProfileUpdateForm
from users.common.common import is_htmx


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profiles/profile.html"
    context_object_name = "profile"

    def get_object(self):
        pk = self.kwargs.get("pk")
        if pk:
            return get_object_or_404(Profile, pk=pk)
        else:
            return get_object_or_404(Profile, user=self.request.user)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = "profiles/update_form_modal.html"
    success_url = reverse_lazy("profiles:index")

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = self.form_class(instance=self.request.user.profile)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if is_htmx(self.request):
            response = HttpResponse()
            response["HX-Redirect"] = self.success_url
            return response
        return response

    def form_invalid(self, form):
        if is_htmx(self.request):
            html = render_to_string(
                self.template_name, {"profile_form": form}, request=self.request
            )
            return JsonResponse({"html": html}, status=400)
        return super().form_invalid(form)
