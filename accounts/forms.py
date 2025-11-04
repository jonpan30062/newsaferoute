from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User
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
