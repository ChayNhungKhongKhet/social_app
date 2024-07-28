from django.contrib import admin
from django.urls import path, include


from home.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="index"),
    path("home/", HomeView.as_view(), name="index"),
    path("users/", include("users.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]
