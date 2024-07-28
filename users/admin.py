from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = get_user_model()
    # Specify the fields to be displayed in the list view of the admin
    list_display = ['email', 'is_staff', 'is_active']
    # Specify the fields to be used as filters in the list view of the admin
    list_filter = ['email', 'is_staff', 'is_active']
    # Define the layout of fields in the detail view of the admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    # Define the layout of fields when adding a new user in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'groups', 'user_permissions'),
        }),
    )
    # Specify the fields to be used in the search functionality of the admin
    search_fields = ['email']
    # Specify the default ordering of the user list in the admin
    ordering = ['email']
admin.site.register(get_user_model(), CustomUserAdmin)