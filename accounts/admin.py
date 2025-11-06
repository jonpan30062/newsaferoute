from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
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
    """Admin configuration for SafetyConcern model with improved approval workflow."""
    list_display = [
        'category_display', 'location_address_short', 'user', 'status_display', 
        'created_at', 'has_photo', 'quick_actions'
    ]
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['location_address', 'description', 'user__email', 'user__first_name', 'user__last_name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'photo_preview', 'status_change_section', 'approve_button']
    autocomplete_fields = ['user']
    list_per_page = 25
    
    fieldsets = (
        ("⚡ Quick Actions", {
            "fields": ("status_change_section", "approve_button"),
            "classes": ("wide",),
            "description": "Quickly change status or approve to create a safety alert on the map"
        }),
        ("Status & Tracking", {
            "fields": ("status", "user", "created_at", "updated_at", "resolved_at"),
            "description": "Current status and tracking information"
        }),
        ("Concern Information", {
            "fields": ("category", "description", "location_address", "latitude", "longitude")
        }),
        ("Photo", {
            "fields": ("photo", "photo_preview"),
            "classes": ("collapse",)
        }),
        ("Admin Notes", {
            "fields": ("admin_notes",),
            "description": "Internal notes for campus security review"
        }),
    )
    
    actions = [
        "approve_and_create_alert", "approve_concerns", "mark_as_in_review", 
        "mark_as_resolved", "mark_as_dismissed", "mark_as_pending"
    ]
    
    def category_display(self, obj):
        """Display category with icon."""
        icons = {
            'broken_light': '💡',
            'unsafe_path': '⚠️',
            'obstruction': '🚧',
            'vandalism': '🔨',
            'maintenance': '🔧',
            'other': '📋',
        }
        icon = icons.get(obj.category, '📋')
        return format_html('{} {}', icon, obj.get_category_display())
    category_display.short_description = "Category"
    
    def location_address_short(self, obj):
        """Display shortened location address."""
        address = obj.location_address[:50] + "..." if len(obj.location_address) > 50 else obj.location_address
        if obj.latitude and obj.longitude:
            map_url = f"https://www.google.com/maps?q={obj.latitude},{obj.longitude}"
            return format_html('<a href="{}" target="_blank" title="{}">📍 {}</a>', 
                             map_url, obj.location_address, address)
        return format_html('📍 {}', address)
    location_address_short.short_description = "Location"
    
    def status_display(self, obj):
        """Display colored status badge with priority indicator."""
        color_map = {
            'pending': ('warning', '🔴'),
            'approved': ('primary', '✅'),
            'in_review': ('info', '👁️'),
            'resolved': ('success', '✓'),
            'dismissed': ('secondary', '✗'),
        }
        color, icon = color_map.get(obj.status, ('secondary', '•'))
        
        # Show priority for pending items
        priority_indicator = ''
        if obj.status == 'pending':
            days_old = (timezone.now() - obj.created_at).days
            if days_old >= 3:
                priority_indicator = ' ⚠️ URGENT'
            elif days_old >= 1:
                priority_indicator = ' ⏰'
        
        return format_html(
            '<span class="badge bg-{}" style="font-size: 0.9em;">{} {}{}</span>',
            color, icon, obj.get_status_display(), priority_indicator
        )
    status_display.short_description = "Status"
    
    def quick_actions(self, obj):
        """Quick action buttons for status changes in list view."""
        from django.urls import reverse
        base_url = reverse('admin:accounts_safetyconcern_quick_status_change')
        
        if obj.status == 'pending':
            return format_html(
                '<a href="{}?status=approved&id={}" class="button" style="background: #28a745; color: white; padding: 5px 10px; '
                'text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 0.85em;">✓ Approve</a> '
                '<a href="{}?status=in_review&id={}" class="button" style="background: #17a2b8; color: white; padding: 5px 10px; '
                'text-decoration: none; border-radius: 3px; font-size: 0.85em;">👁️ Review</a>',
                base_url, obj.id, base_url, obj.id
            )
        elif obj.status == 'in_review':
            return format_html(
                '<a href="{}?status=approved&id={}" class="button" style="background: #28a745; color: white; padding: 5px 10px; '
                'text-decoration: none; border-radius: 3px; margin-right: 5px; font-size: 0.85em;">✓ Approve</a> '
                '<a href="{}?status=dismissed&id={}" class="button" style="background: #6c757d; color: white; padding: 5px 10px; '
                'text-decoration: none; border-radius: 3px; font-size: 0.85em;">✗ Dismiss</a>',
                base_url, obj.id, base_url, obj.id
            )
        elif obj.status == 'approved':
            return format_html(
                '<a href="{}?status=resolved&id={}" class="button" style="background: #28a745; color: white; padding: 5px 10px; '
                'text-decoration: none; border-radius: 3px; font-size: 0.85em;">✓ Resolve</a>',
                base_url, obj.id
            )
        return format_html('<span style="color: #6c757d;">—</span>')
    quick_actions.short_description = "Quick Actions"
    
    def has_photo(self, obj):
        """Display if photo is available with link."""
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank" style="color: #28a745;">📷 View Photo</a>',
                obj.photo.url
            )
        return format_html('<span style="color: #6c757d;">No photo</span>')
    has_photo.short_description = "Photo"
    
    def photo_preview(self, obj):
        """Display photo preview in admin."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.photo.url
            )
        return format_html('<span style="color: #6c757d;">No photo uploaded</span>')
    photo_preview.short_description = "Photo Preview"
    
    def approve_button(self, obj):
        """Display approve button if concern is pending."""
        if obj.pk and obj.status == 'pending':
            return format_html(
                '<a class="button" href="/admin/accounts/safetyconcern/{}/approve/" '
                'style="background: #417690; color: white; padding: 10px 20px; '
                'text-decoration: none; border-radius: 5px; display: inline-block; '
                'font-weight: bold;">'
                '✓ Approve & Create Safety Alert on Map</a>',
                obj.pk
            )
        elif obj.status == 'resolved':
            return format_html(
                '<div style="color: green; font-weight: bold;">✓ Already approved and published</div>'
            )
        else:
            return format_html(
                '<div style="color: gray;">Concern status: {}</div>',
                obj.get_status_display()
            )
    approve_button.short_description = "Approve This Concern"
    
    def get_urls(self):
        """Add custom URL for approving individual concerns."""
        urls = super().get_urls()
        custom_urls = [
            path('<int:concern_id>/approve/', self.admin_site.admin_view(self.approve_concern_view), name='safetyconcern_approve'),
        ]
        return custom_urls + urls
    
    def approve_concern_view(self, request, concern_id):
        """Custom view to approve a single concern."""
        try:
            concern = SafetyConcern.objects.get(pk=concern_id)
            
            # Check if coordinates are available
            if not concern.latitude or not concern.longitude:
                messages.error(request, "Cannot approve: Missing GPS coordinates.")
                return redirect('admin:accounts_safetyconcern_change', concern_id)
            
            # Map concern category to alert type
            category_to_alert_type = {
                'broken_light': 'maintenance',
                'unsafe_path': 'hazard',
                'obstruction': 'hazard',
                'vandalism': 'other',
                'maintenance': 'maintenance',
                'other': 'other',
            }
            
            # Create SafetyAlert from the concern as a circle (250 feet radius)
            # 250 feet in meters = 76.2 meters
            CIRCLE_RADIUS_METERS = 76.2
            alert = SafetyAlert.objects.create(
                title=f"{concern.get_category_display()} - {concern.location_address[:50]}",
                description=concern.description,
                address=concern.location_address,
                alert_type=category_to_alert_type.get(concern.category, 'other'),
                severity='medium',
                location_type='circle',
                latitude=concern.latitude,
                longitude=concern.longitude,
                radius=CIRCLE_RADIUS_METERS,
                is_active=True,
                created_by=request.user
            )
            
            # Mark concern as resolved
            concern.status = 'resolved'
            concern.resolved_at = timezone.now()
            concern.admin_notes = f"Approved and converted to SafetyAlert #{alert.id}"
            concern.save()
            
            messages.success(
                request,
                f"✓ Success! Safety Alert #{alert.id} created and published on the map. "
                f"View it at <a href='/admin/accounts/safetyalert/{alert.id}/change/'>Safety Alert #{alert.id}</a>"
            )
            
        except SafetyConcern.DoesNotExist:
            messages.error(request, "Safety concern not found.")
        except Exception as e:
            messages.error(request, f"Error creating alert: {str(e)}")
        
        return redirect('admin:accounts_safetyconcern_change', concern_id)
    
    def approve_and_create_alert(self, request, queryset):
        """Approve selected concerns and create SafetyAlerts from them."""
        created_count = 0
        error_count = 0
        
        for concern in queryset:
            # Check if coordinates are available
            if not concern.latitude or not concern.longitude:
                error_count += 1
                continue
            
            # Map concern category to alert type
            category_to_alert_type = {
                'broken_light': 'maintenance',
                'unsafe_path': 'hazard',
                'obstruction': 'hazard',
                'vandalism': 'other',
                'maintenance': 'maintenance',
                'other': 'other',
            }
            
            # Create SafetyAlert from the concern as a circle (250 feet radius)
            # 250 feet in meters = 76.2 meters
            CIRCLE_RADIUS_METERS = 76.2
            alert = SafetyAlert.objects.create(
                title=f"{concern.get_category_display()} - {concern.location_address[:50]}",
                description=concern.description,
                address=concern.location_address,
                alert_type=category_to_alert_type.get(concern.category, 'other'),
                severity='medium',  # Default to medium, admin can adjust
                location_type='circle',
                latitude=concern.latitude,
                longitude=concern.longitude,
                radius=CIRCLE_RADIUS_METERS,
                is_active=True,
                created_by=request.user
            )
            
            # Mark concern as resolved
            concern.status = 'resolved'
            concern.resolved_at = timezone.now()
            concern.admin_notes = f"Approved and converted to SafetyAlert #{alert.id}"
            concern.save()
            
            created_count += 1
        
        # Provide feedback
        if created_count > 0:
            self.message_user(
                request,
                f"✓ Successfully created {created_count} safety alert(s) from approved concerns.",
                level='success'
            )
        if error_count > 0:
            self.message_user(
                request,
                f"⚠ {error_count} concern(s) skipped (missing GPS coordinates).",
                level='warning'
            )
    approve_and_create_alert.short_description = "✓ Approve & Create Safety Alert on Map"
    
    def status_change_section(self, obj):
        """Interactive status change section in detail view."""
        from django.urls import reverse
        
        if obj.pk is None:
            return format_html('<p style="color: #fff;">Save the concern first to change status</p>')
        
        # Color gradients for each status (light to dark for gradient effect)
        color_gradients = {
            'warning': ('ffb020', 'ff9500'),     # Orange gradient
            'primary': ('5b80d2', '417690'),      # Blue gradient (matches admin theme)
            'info': ('5b80d2', '417690'),        # Blue gradient
            'success': ('28a745', '1e7e34'),      # Green gradient
            'secondary': ('6c757d', '5a6268'),   # Gray gradient
        }
        
        status_options = [
            ('pending', 'Pending Review', 'warning', '🔴'),
            ('approved', 'Approved', 'primary', '✅'),
            ('in_review', 'In Review', 'info', '👁️'),
            ('resolved', 'Resolved', 'success', '✓'),
            ('dismissed', 'Dismissed', 'secondary', '✗'),
        ]
        
        base_url = reverse('admin:accounts_safetyconcern_quick_status_change')
        current_status = obj.status
        buttons = []
        
        for status, label, color, icon in status_options:
            grad_start, grad_end = color_gradients.get(color, ('6c757d', '5a6268'))
            
            if status == current_status:
                # Current status - highlighted with white border
                buttons.append(format_html(
                    '<span style="background: linear-gradient(135deg, #{} 0%, #{} 100%); color: white; padding: 10px 18px; '
                    'border-radius: 6px; margin-right: 8px; margin-bottom: 8px; font-weight: bold; display: inline-block; '
                    'box-shadow: 0 2px 6px rgba(0,0,0,0.3); border: 2px solid #fff;">{} Current: {}</span>',
                    grad_start, grad_end, icon, label
                ))
            else:
                # Other statuses - clickable buttons with hover effect
                buttons.append(format_html(
                    '<a href="{}?status={}&id={}" style="background: linear-gradient(135deg, #{} 0%, #{} 100%); color: white; '
                    'padding: 10px 18px; text-decoration: none; border-radius: 6px; margin-right: 8px; display: inline-block; '
                    'margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: all 0.2s; border: 1px solid rgba(255,255,255,0.2);" '
                    'onmouseover="this.style.transform=\'translateY(-2px)\'; this.style.boxShadow=\'0 4px 8px rgba(0,0,0,0.3)\';" '
                    'onmouseout="this.style.transform=\'translateY(0)\'; this.style.boxShadow=\'0 2px 4px rgba(0,0,0,0.2)\';" '
                    'onclick="return confirm(\'Change status to {}?\')">{} {}</a>',
                    base_url, status, obj.id, grad_start, grad_end, label, icon, label
                ))
        
        return format_html(
            '<div style="padding: 20px; background: linear-gradient(135deg, #264b5d 0%, #417690 100%); border-radius: 8px; '
            'margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);">'
            '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">'
            '<h4 style="margin: 0; color: #fff; font-size: 1.15em; font-weight: 600; '
            'display: flex; align-items: center; gap: 8px;">'
            '<span style="font-size: 1.3em;">⚡</span> Quick Status Change</h4>'
            '</div>'
            '<p style="color: rgba(255,255,255,0.75); font-size: 0.875em; margin: 0 0 18px 0; padding: 8px 12px; '
            'background: rgba(255,255,255,0.08); border-radius: 4px; border-left: 3px solid rgba(255,255,255,0.3); '
            'line-height: 1.5; font-style: italic;">'
            '<span style="margin-right: 6px;">💡</span>Click any status button below to change it instantly</p>'
            '<div style="margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 8px;">{}</div>'
            '<p style="color: rgba(255,255,255,0.85); font-size: 0.85em; margin: 12px 0 0 0; padding-top: 12px; '
            'border-top: 1px solid rgba(255,255,255,0.2);">'
            'Current status: <strong style="color: #fff; font-weight: 600;">{}</strong></p>'
            '</div>',
            format_html(''.join(buttons)),
            obj.get_status_display()
        )
    status_change_section.short_description = "Status Actions"
    
    def approve_concerns(self, request, queryset):
        """Approve selected concerns (moves from pending to approved)."""
        count = queryset.count()
        updated = queryset.update(status='approved')
        self.message_user(
            request, 
            f"✅ {updated} concern(s) approved successfully and ready for action.",
            level='success'
        )
    approve_concerns.short_description = "✅ Approve selected concerns"
    
    def mark_as_in_review(self, request, queryset):
        """Mark selected concerns as in review."""
        updated = queryset.update(status='in_review')
        self.message_user(
            request, 
            f"👁️ {updated} concern(s) marked as in review.",
            level='info'
        )
    mark_as_in_review.short_description = "👁️ Mark as in review"
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected concerns as resolved."""
        now = timezone.now()
        updated = queryset.update(status='resolved', resolved_at=now)
        self.message_user(
            request, 
            f"✓ {updated} concern(s) marked as resolved.",
            level='success'
        )
    mark_as_resolved.short_description = "✓ Mark as resolved"
    
    def mark_as_dismissed(self, request, queryset):
        """Mark selected concerns as dismissed."""
        updated = queryset.update(status='dismissed')
        self.message_user(
            request, 
            f"✗ {updated} concern(s) marked as dismissed.",
            level='warning'
        )
    mark_as_dismissed.short_description = "✗ Mark as dismissed"
    
    def mark_as_pending(self, request, queryset):
        """Mark selected concerns as pending."""
        updated = queryset.update(status='pending')
        self.message_user(
            request, 
            f"🔴 {updated} concern(s) marked as pending.",
            level='warning'
        )
    mark_as_pending.short_description = "🔴 Mark as pending"
    
    def get_urls(self):
        """Add custom URL for quick status changes."""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('quick-status-change/', self.admin_site.admin_view(self.quick_status_change_view), 
                 name='accounts_safetyconcern_quick_status_change'),
        ]
        return custom_urls + urls
    
    def quick_status_change_view(self, request):
        """Handle quick status changes from list view."""
        from django.shortcuts import redirect
        from django.contrib import messages
        from django.urls import reverse
        
        concern_id = request.GET.get('id')
        new_status = request.GET.get('status')
        
        if concern_id and new_status:
            try:
                concern = SafetyConcern.objects.get(id=concern_id)
                old_status = concern.status
                concern.status = new_status
                
                if new_status == 'resolved' and not concern.resolved_at:
                    concern.resolved_at = timezone.now()
                
                concern.save()
                
                status_names = {
                    'pending': 'Pending Review',
                    'approved': 'Approved',
                    'in_review': 'In Review',
                    'resolved': 'Resolved',
                    'dismissed': 'Dismissed',
                }
                
                messages.success(
                    request,
                    f"✓ Status changed from '{status_names.get(old_status, old_status)}' to '{status_names.get(new_status, new_status)}'"
                )
            except SafetyConcern.DoesNotExist:
                messages.error(request, "Safety concern not found.")
        
        return redirect(reverse('admin:accounts_safetyconcern_changelist'))
