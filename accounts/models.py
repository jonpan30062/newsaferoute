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
