from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, SafetyConcern
import re


class RegistrationForm(UserCreationForm):
    """
    Form for user registration with email, full name, and password validation.
    Password must be at least 8 characters and contain at least 1 number.
    """
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min. 8 characters, 1 number)'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        """Validate that the email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_password1(self):
        """
        Validate password meets security requirements:
        - At least 8 characters
        - At least 1 number
        """
        password = self.cleaned_data.get('password1')

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least 1 number.")

        return password

    def save(self, commit=True):
        """Create user with email as username."""
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Custom login form that uses email instead of username.
    """
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    error_messages = {
        'invalid_login': "Please enter a correct email and password. Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    Allows users to update their first name, last name, and email.
    """
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        """Store the user instance for validation."""
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        """Validate that the email is unique (excluding current user)."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        """Update user profile and sync username with email."""
        user = super().save(commit=False)
        # Keep username in sync with email
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SafetyConcernForm(forms.ModelForm):
    """
    Form for submitting safety concerns.
    Supports GPS location auto-fill or manual address entry.
    """
    use_gps = forms.BooleanField(
        required=False,
        initial=False,
        label="Use Current Location (GPS)",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'use_gps'
        }),
        help_text="Check this to automatically use your current GPS location"
    )
    
    location_address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the location address or description (e.g., "Near Engineering Building, Main Walkway")',
            'rows': 3
        }),
        label="Location",
        help_text="Describe where the safety concern is located"
    )
    
    latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(),
        max_digits=9,
        decimal_places=6
    )
    
    longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(),
        max_digits=9,
        decimal_places=6
    )
    
    category = forms.ChoiceField(
        required=True,
        choices=SafetyConcern.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Category"
    )
    
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Provide a detailed description of the safety concern...',
            'rows': 5
        }),
        label="Description",
        help_text="Please provide as much detail as possible"
    )
    
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label="Photo (Optional)",
        help_text="Upload a photo if available (JPG, PNG, etc.)"
    )
    
    class Meta:
        model = SafetyConcern
        fields = ['location_address', 'latitude', 'longitude', 'category', 'description', 'photo']
    
    def clean_description(self):
        """Validate description is not too short."""
        description = self.cleaned_data.get('description')
        if description and len(description.strip()) < 10:
            raise ValidationError("Please provide a more detailed description (at least 10 characters).")
        return description
    
    def clean_location_address(self):
        """Validate location address is provided."""
        location = self.cleaned_data.get('location_address')
        if not location or len(location.strip()) < 5:
            raise ValidationError("Please provide a more specific location description (at least 5 characters).")
        return location
    
    def clean_photo(self):
        """Validate photo file size and type."""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("Photo file size must be less than 5MB.")
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            file_name = photo.name.lower()
            if not any(file_name.endswith(ext) for ext in valid_extensions):
                raise ValidationError("Photo must be a valid image file (JPG, PNG, GIF, or WebP).")
        
        return photo
