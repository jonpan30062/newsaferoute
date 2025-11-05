from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, Building, Favorite, SavedRoute, SafetyAlert, SafetyConcern


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


@admin.register(SafetyAlert)
class SafetyAlertAdmin(admin.ModelAdmin):
    """Admin configuration for SafetyAlert model."""
    list_display = ["title", "alert_type", "severity", "location_type", "is_active_display", "status_display", "created_at", "created_by"]
    list_filter = ["alert_type", "severity", "is_active", "location_type", "created_at", "created_by"]
    search_fields = ["title", "description"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at", "status_display"]
    autocomplete_fields = ["created_by"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "description", "alert_type", "severity")
        }),
        ("Location", {
            "fields": ("location_type", "latitude", "longitude", "radius", "polygon_coordinates"),
            "description": "For circle type, provide radius in meters. For polygon type, provide JSON array of coordinates."
        }),
        ("Status & Dates", {
            "fields": ("is_active", "start_date", "end_date", "status_display")
        }),
        ("Metadata", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def is_active_display(self, obj):
        """Display colored active status."""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_display.short_description = "Active"
    
    def status_display(self, obj):
        """Display current status based on dates and active flag."""
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactive</span>')
        
        now = timezone.now()
        if obj.start_date and now < obj.start_date:
            return format_html('<span style="color: orange;">Scheduled (starts {})</span>', obj.start_date.strftime("%Y-%m-%d %H:%M"))
        if obj.end_date and now > obj.end_date:
            return format_html('<span style="color: red;">Expired (ended {})</span>', obj.end_date.strftime("%Y-%m-%d %H:%M"))
        if obj.is_currently_active():
            return format_html('<span style="color: green;">Currently Active</span>')
        return format_html('<span style="color: gray;">Unknown</span>')
    status_display.short_description = "Status"
    
    actions = ["activate_alerts", "deactivate_alerts", "mark_as_expired"]
    
    def activate_alerts(self, request, queryset):
        """Activate selected alerts."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} alert(s) activated successfully.")
    activate_alerts.short_description = "Activate selected alerts"
    
    def deactivate_alerts(self, request, queryset):
        """Deactivate selected alerts."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} alert(s) deactivated successfully.")
    deactivate_alerts.short_description = "Deactivate selected alerts"
    
    def mark_as_expired(self, request, queryset):
        """Mark selected alerts as expired by setting end_date to now."""
        now = timezone.now()
        updated = queryset.update(end_date=now)
        self.message_user(request, f"{updated} alert(s) marked as expired.")
    mark_as_expired.short_description = "Mark as expired"


@admin.register(SafetyConcern)
class SafetyConcernAdmin(admin.ModelAdmin):
    """Admin configuration for SafetyConcern model."""
    list_display = [
        'category_display', 'location_address_short', 'user', 'status_display', 
        'created_at', 'has_photo'
    ]
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['location_address', 'description', 'user__email', 'user__first_name', 'user__last_name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'photo_preview']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ("Concern Information", {
            "fields": ("category", "description", "location_address", "latitude", "longitude")
        }),
        ("Photo", {
            "fields": ("photo", "photo_preview"),
            "classes": ("collapse",)
        }),
        ("Status & Tracking", {
            "fields": ("status", "user", "created_at", "updated_at", "resolved_at")
        }),
        ("Admin Notes", {
            "fields": ("admin_notes",),
            "description": "Internal notes for campus security review"
        }),
    )
    
    actions = ["mark_as_pending", "mark_as_in_review", "mark_as_resolved", "mark_as_dismissed"]
    
    def category_display(self, obj):
        """Display category with icon."""
        return obj.get_category_display()
    category_display.short_description = "Category"
    
    def location_address_short(self, obj):
        """Display shortened location address."""
        return obj.location_address[:50] + "..." if len(obj.location_address) > 50 else obj.location_address
    location_address_short.short_description = "Location"
    
    def status_display(self, obj):
        """Display colored status badge."""
        color_map = {
            'pending': 'warning',
            'in_review': 'info',
            'resolved': 'success',
            'dismissed': 'secondary',
        }
        color = color_map.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = "Status"
    
    def has_photo(self, obj):
        """Display if photo is available."""
        if obj.photo:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: gray;">✗ No</span>')
    has_photo.short_description = "Photo"
    has_photo.boolean = True
    
    def photo_preview(self, obj):
        """Display photo preview in admin."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px;" />',
                obj.photo.url
            )
        return "No photo uploaded"
    photo_preview.short_description = "Photo Preview"
    
    def mark_as_pending(self, request, queryset):
        """Mark selected concerns as pending."""
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} concern(s) marked as pending.")
    mark_as_pending.short_description = "Mark as pending"
    
    def mark_as_in_review(self, request, queryset):
        """Mark selected concerns as in review."""
        updated = queryset.update(status='in_review')
        self.message_user(request, f"{updated} concern(s) marked as in review.")
    mark_as_in_review.short_description = "Mark as in review"
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected concerns as resolved."""
        now = timezone.now()
        updated = queryset.update(status='resolved', resolved_at=now)
        self.message_user(request, f"{updated} concern(s) marked as resolved.")
    mark_as_resolved.short_description = "Mark as resolved"
    
    def mark_as_dismissed(self, request, queryset):
        """Mark selected concerns as dismissed."""
        updated = queryset.update(status='dismissed')
        self.message_user(request, f"{updated} concern(s) marked as dismissed.")
    mark_as_dismissed.short_description = "Mark as dismissed"
