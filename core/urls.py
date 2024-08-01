from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from home.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="index"),
    path("home/", HomeView.as_view(), name="index"),
    path("users/", include("users.urls")),
    path("profiles/", include("profiles.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)