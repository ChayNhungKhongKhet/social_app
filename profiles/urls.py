from django.urls import path

from .views import ProfileView, ProfileUpdateView


app_name = "profiles"

urlpatterns = [
    path("", ProfileView.as_view(), name="index"),  # Default to current user's profile
    path("<int:pk>/", ProfileView.as_view(), name="index_with_pk"),
    path("update/", ProfileUpdateView.as_view(), name="update"),
]