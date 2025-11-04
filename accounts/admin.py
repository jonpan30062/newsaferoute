from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Building, Favorite, SavedRoute


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin configuration."""
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active", "date_joined"]
    list_filter = ["is_staff", "is_active", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    # Update fieldsets to show email prominently
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name", "last_name", "password1", "password2"),
        }),
    )


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    """Admin configuration for Building model."""
    list_display = ["name", "code", "address", "latitude", "longitude"]
    list_filter = ["created_at"]
    search_fields = ["name", "code", "address"]
    ordering = ["name"]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin configuration for Favorite model."""
    list_display = ["user", "building", "custom_name", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "building__name", "building__code", "custom_name"]
    ordering = ["-created_at"]
    autocomplete_fields = ["user", "building"]


@admin.register(SavedRoute)
class SavedRouteAdmin(admin.ModelAdmin):
    """Admin configuration for SavedRoute model."""
    list_display = ["user", "name", "origin_name", "destination_name", "distance_text", "duration_text", "created_at", "last_used"]
    list_filter = ["created_at", "last_used"]
    search_fields = ["user__email", "name", "origin_name", "destination_name", "destination_building__name"]
    ordering = ["-last_used", "-created_at"]
    autocomplete_fields = ["user", "destination_building"]
    readonly_fields = ["created_at", "updated_at"]
