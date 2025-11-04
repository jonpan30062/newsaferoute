from django.contrib.auth.models import AbstractUser
from django.db import models


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
