from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import json


class User(AbstractUser):
    """
    Custom User model that uses email as the username field.
    Includes full name fields for user registration.
    """
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=150, verbose_name="First Name")
    last_name = models.CharField(max_length=150, verbose_name="Last Name")

    # Use email as the username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the first_name and last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Building(models.Model):
    """
    Model representing a campus building with location information.
    Supports search by name or building code.
    """
    name = models.CharField(max_length=255, verbose_name="Building Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Building Code")
    address = models.TextField(verbose_name="Address")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Building"
        verbose_name_plural = "Buildings"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Favorite(models.Model):
    """
    Model representing a user's favorite building.
    Users can bookmark buildings for quick access.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='favorited_by')
    custom_name = models.CharField(max_length=255, blank=True, verbose_name="Custom Name")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        ordering = ['-created_at']
        unique_together = ('user', 'building')

    def __str__(self):
        return f"{self.user.email} - {self.building.name}"

    def get_display_name(self):
        """Return custom name if set, otherwise return building name."""
        return self.custom_name if self.custom_name else self.building.name


class SavedRoute(models.Model):
    """
    Model representing a user's saved route.
    Stores complete route information including origin, destination, and route data.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_routes')
    name = models.CharField(max_length=255, verbose_name="Route Name")

    # Origin coordinates
    origin_lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Origin Latitude")
    origin_lng = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Origin Longitude")
    origin_name = models.CharField(max_length=255, verbose_name="Origin Name", default="My Location")

    # Destination (can be linked to a building or custom location)
    destination_building = models.ForeignKey(
        Building,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='routes_to_here'
    )
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Destination Latitude")
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Destination Longitude")
    destination_name = models.CharField(max_length=255, verbose_name="Destination Name")

    # Route details
    distance_text = models.CharField(max_length=50, verbose_name="Distance")
    duration_text = models.CharField(max_length=50, verbose_name="Duration")
    distance_value = models.IntegerField(verbose_name="Distance in meters")
    duration_value = models.IntegerField(verbose_name="Duration in seconds")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="Last Used")

    class Meta:
        verbose_name = "Saved Route"
        verbose_name_plural = "Saved Routes"
        ordering = ['-last_used', '-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    def get_destination_display(self):
        """Return destination building name if linked, otherwise custom name."""
        if self.destination_building:
            return f"{self.destination_building.name} ({self.destination_building.code})"
        return self.destination_name


class SafetyAlert(models.Model):
    """
    Model representing a safety alert (construction, emergency, etc.)
    that can be displayed on the map as icons or colored zones.
    """
    ALERT_TYPE_CHOICES = [
        ('construction', 'Construction'),
        ('emergency', 'Emergency'),
        ('maintenance', 'Maintenance'),
        ('hazard', 'Hazard'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    LOCATION_TYPE_CHOICES = [
        ('point', 'Point'),
        ('circle', 'Circle'),
        ('polygon', 'Polygon'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="Alert Title")
    description = models.TextField(verbose_name="Description")
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name="Address",
        help_text="Address for geocoding (optional if coordinates are provided)"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        default='other',
        verbose_name="Alert Type"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        verbose_name="Severity"
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default='point',
        verbose_name="Location Type"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude",
        help_text="Optional - will be geocoded from address if not provided"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude",
        help_text="Optional - will be geocoded from address if not provided"
    )
    radius = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Radius (meters)",
        help_text="Required for circle location type"
    )
    polygon_coordinates = models.TextField(
        null=True,
        blank=True,
        verbose_name="Polygon Coordinates",
        help_text="JSON array of [lat, lng] pairs: [[lat1, lng1], [lat2, lng2], ...]"
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Start Date")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="End Date")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_alerts',
        verbose_name="Created By"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Safety Alert"
        verbose_name_plural = "Safety Alerts"
        ordering = ['-severity', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'severity']),
            models.Index(fields=['alert_type', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_alert_type_display()})"
    
    def is_currently_active(self):
        """Check if alert is currently active based on dates and is_active flag."""
        if not self.is_active:
            return False
        
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def get_color(self):
        """Return hex color code based on severity."""
        color_map = {
            'low': '#fbbf24',      # Yellow
            'medium': '#f59e0b',   # Orange
            'high': '#ef4444',     # Red
            'critical': '#dc2626',  # Dark Red
        }
        return color_map.get(self.severity, '#f59e0b')
    
    def get_icon_url(self):
        """Return appropriate marker icon based on alert_type and severity."""
        # Use Google Maps default icons with custom colors
        # For now, we'll use colored markers based on severity
        # This can be enhanced with custom icons later
        icon_map = {
            'construction': 'http://maps.google.com/mapfiles/ms/icons/construction.png',
            'emergency': 'http://maps.google.com/mapfiles/ms/icons/alert.png',
            'maintenance': 'http://maps.google.com/mapfiles/ms/icons/tools.png',
            'hazard': 'http://maps.google.com/mapfiles/ms/icons/warning.png',
            'other': 'http://maps.google.com/mapfiles/ms/icons/info.png',
        }
        return icon_map.get(self.alert_type, icon_map['other'])
    
    def get_polygon_coordinates(self):
        """Parse and return polygon coordinates as list (if polygon type)."""
        if self.location_type != 'polygon' or not self.polygon_coordinates:
            return None
        
        try:
            return json.loads(self.polygon_coordinates)
        except json.JSONDecodeError:
            return None
    
    def clean(self):
        """Validate model fields."""
        from django.core.exceptions import ValidationError
        
        # Validate circle location type has radius
        if self.location_type == 'circle' and not self.radius:
            raise ValidationError({
                'radius': 'Radius is required for circle location type.'
            })
        
        # Validate polygon location type has coordinates
        if self.location_type == 'polygon':
            if not self.polygon_coordinates:
                raise ValidationError({
                    'polygon_coordinates': 'Polygon coordinates are required for polygon location type.'
                })
            # Validate JSON format
            try:
                coords = json.loads(self.polygon_coordinates)
                if not isinstance(coords, list) or len(coords) < 3:
                    raise ValidationError({
                        'polygon_coordinates': 'Polygon must have at least 3 coordinate pairs.'
                    })
            except json.JSONDecodeError:
                raise ValidationError({
                    'polygon_coordinates': 'Invalid JSON format for polygon coordinates.'
                })
        
        # Validate date range
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        # Validate coordinates if provided
        if self.latitude is not None:
            try:
                if not (-90 <= float(self.latitude) <= 90):
                    raise ValidationError({
                        'latitude': 'Latitude must be between -90 and 90.'
                    })
            except (ValueError, TypeError):
                raise ValidationError({
                    'latitude': 'Invalid latitude value.'
                })
        
        if self.longitude is not None:
            try:
                if not (-180 <= float(self.longitude) <= 180):
                    raise ValidationError({
                        'longitude': 'Longitude must be between -180 and 180.'
                    })
            except (ValueError, TypeError):
                raise ValidationError({
                    'longitude': 'Invalid longitude value.'
                })
        
        # Ensure either address or coordinates are provided
        if not self.address and (self.latitude is None or self.longitude is None):
            raise ValidationError({
                'address': 'Either address or coordinates must be provided.'
            })


class SafetyConcern(models.Model):
    """
    Model representing a user-submitted safety concern.
    Users can report issues like broken lights, unsafe paths, etc.
    """
    CATEGORY_CHOICES = [
        ('broken_light', 'Broken Light'),
        ('unsafe_path', 'Unsafe Path'),
        ('obstruction', 'Obstruction'),
        ('vandalism', 'Vandalism'),
        ('maintenance', 'Maintenance Issue'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    # User information
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_concerns',
        verbose_name="Submitted By"
    )
    
    # Location information
    location_address = models.TextField(
        verbose_name="Location Address",
        help_text="Address or description of the location"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude",
        help_text="Auto-filled from GPS if available"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude",
        help_text="Auto-filled from GPS if available"
    )
    
    # Concern details
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name="Category"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Detailed description of the safety concern"
    )
    photo = models.ImageField(
        upload_to='safety_concerns/',
        null=True,
        blank=True,
        verbose_name="Photo",
        help_text="Optional photo of the safety concern"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Submitted At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Resolved At"
    )
    
    # Admin notes
    admin_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Admin Notes",
        help_text="Internal notes from campus security"
    )
    
    class Meta:
        verbose_name = "Safety Concern"
        verbose_name_plural = "Safety Concerns"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.location_address[:50]}"
    
    def get_status_badge_color(self):
        """Return Bootstrap badge color class based on status."""
        color_map = {
            'pending': 'warning',
            'approved': 'primary',
            'in_review': 'info',
            'resolved': 'success',
            'dismissed': 'secondary',
        }
        return color_map.get(self.status, 'secondary')
