from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from .forms import RegistrationForm, LoginForm
from .models import Building


def register_view(request):
    """
    User registration view.
    - Displays registration form
    - Validates password requirements (8+ chars, 1 number)
    - Creates user profile in database
    - Automatically logs in user after successful registration
    - Redirects to dashboard
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create and save the user
            user = form.save()

            # Automatically log in the user
            login(request, user)

            # Success message
            messages.success(
                request,
                f'Welcome, {user.get_full_name()}! Your account has been created successfully.'
            )

            # Redirect to dashboard
            return redirect('dashboard')
        else:
            # Form has errors - they will be displayed in the template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    User login view.
    - Displays login form
    - Validates credentials via backend
    - Shows clear error messages for incorrect credentials
    - Loads user dashboard with saved data on successful login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        # Get the email and password from POST data for custom authentication
        email = request.POST.get('username')  # LoginForm uses 'username' field for email
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # User credentials are valid
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')

            # Redirect to dashboard or to 'next' parameter if provided
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            # Invalid credentials - show clear error message
            messages.error(
                request,
                'Invalid email or password. Please check your credentials and try again.'
            )
            form = LoginForm(request)

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def dashboard_view(request):
    """
    Main dashboard view for logged-in users.
    Displays user's saved buildings and personalized settings.
    Requires authentication - redirects to login if not authenticated.
    """
    context = {
        'user': request.user,
        'full_name': request.user.get_full_name(),
    }
    return render(request, 'accounts/dashboard.html', context)


def logout_view(request):
    """
    Logout view - logs out the user and redirects to home page.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def home_view(request):
    """
    Home page view - landing page for the application.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


def map_view(request):
    """
    Map view - displays interactive map with building search and routing.
    """
    from django.conf import settings
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'accounts/map.html', context)


def building_search_api(request):
    """
    API endpoint for searching buildings by name or code.
    Supports partial matching (case-insensitive).
    Returns JSON list of matching buildings.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        # Return all buildings if no query provided
        buildings = Building.objects.all()[:20]  # Limit to 20 results
    else:
        # Search by name or code (partial match, case-insensitive)
        buildings = Building.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )[:20]
    
    # Format results as JSON
    results = []
    for building in buildings:
        results.append({
            'id': building.id,
            'name': building.name,
            'code': building.code,
            'address': building.address,
            'latitude': float(building.latitude),
            'longitude': float(building.longitude),
            'description': building.description,
        })
    
    return JsonResponse({
        'success': True,
        'count': len(results),
        'buildings': results
    })
