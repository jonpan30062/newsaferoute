from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm
from .models import Building, Favorite, SavedRoute, SafetyAlert


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
    favorites_count = Favorite.objects.filter(user=request.user).count()
    saved_routes_count = SavedRoute.objects.filter(user=request.user).count()

    context = {
        'user': request.user,
        'full_name': request.user.get_full_name(),
        'favorites_count': favorites_count,
        'saved_routes_count': saved_routes_count,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def settings_view(request):
    """
    Settings/Profile update view for logged-in users.
    Allows users to update their profile information (name, email).
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your profile has been updated successfully!'
            )
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {
        'user': request.user,
        'form': form,
    }
    return render(request, 'accounts/settings.html', context)


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


@login_required
@require_http_methods(["POST"])
def toggle_favorite_api(request):
    """
    API endpoint to toggle a building as favorite.
    If building is already favorited, remove it. Otherwise, add it.
    """
    import json

    try:
        data = json.loads(request.body)
        building_id = data.get('building_id')

        if not building_id:
            return JsonResponse({
                'success': False,
                'error': 'Building ID is required'
            }, status=400)

        # Check if building exists
        try:
            building = Building.objects.get(id=building_id)
        except Building.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Building not found'
            }, status=404)

        # Check if already favorited
        favorite = Favorite.objects.filter(user=request.user, building=building).first()

        if favorite:
            # Remove from favorites
            favorite.delete()
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'message': f'{building.name} removed from favorites'
            })
        else:
            # Add to favorites
            favorite = Favorite.objects.create(user=request.user, building=building)
            return JsonResponse({
                'success': True,
                'action': 'added',
                'message': f'{building.name} added to favorites',
                'favorite_id': favorite.id
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def user_favorites_api(request):
    """
    API endpoint to get all favorites for the current user.
    Returns list of favorited buildings with custom names if set.
    """
    favorites = Favorite.objects.filter(user=request.user).select_related('building')

    results = []
    for favorite in favorites:
        results.append({
            'id': favorite.id,
            'building_id': favorite.building.id,
            'building_name': favorite.building.name,
            'building_code': favorite.building.code,
            'custom_name': favorite.custom_name,
            'display_name': favorite.get_display_name(),
            'address': favorite.building.address,
            'latitude': float(favorite.building.latitude),
            'longitude': float(favorite.building.longitude),
            'description': favorite.building.description,
            'created_at': favorite.created_at.isoformat(),
        })

    return JsonResponse({
        'success': True,
        'count': len(results),
        'favorites': results
    })


@login_required
@require_http_methods(["POST"])
def rename_favorite_api(request):
    """
    API endpoint to rename a favorite (set custom name).
    """
    import json

    try:
        data = json.loads(request.body)
        favorite_id = data.get('favorite_id')
        custom_name = data.get('custom_name', '').strip()

        if not favorite_id:
            return JsonResponse({
                'success': False,
                'error': 'Favorite ID is required'
            }, status=400)

        # Get favorite and verify ownership
        try:
            favorite = Favorite.objects.get(id=favorite_id, user=request.user)
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Favorite not found or you do not have permission'
            }, status=404)

        # Update custom name
        favorite.custom_name = custom_name
        favorite.save()

        return JsonResponse({
            'success': True,
            'message': 'Favorite renamed successfully',
            'custom_name': custom_name,
            'display_name': favorite.get_display_name()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_favorite_api(request):
    """
    API endpoint to delete a favorite.
    """
    import json

    try:
        data = json.loads(request.body)
        favorite_id = data.get('favorite_id')

        if not favorite_id:
            return JsonResponse({
                'success': False,
                'error': 'Favorite ID is required'
            }, status=400)

        # Get favorite and verify ownership
        try:
            favorite = Favorite.objects.get(id=favorite_id, user=request.user)
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Favorite not found or you do not have permission'
            }, status=404)

        building_name = favorite.building.name
        favorite.delete()

        return JsonResponse({
            'success': True,
            'message': f'{building_name} removed from favorites'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def check_favorite_api(request):
    """
    API endpoint to check if a building is favorited by the current user.
    """
    building_id = request.GET.get('building_id')

    if not building_id:
        return JsonResponse({
            'success': False,
            'error': 'Building ID is required'
        }, status=400)

    is_favorite = Favorite.objects.filter(
        user=request.user,
        building_id=building_id
    ).exists()

    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite
    })


@login_required
def favorites_view(request):
    """
    View to display all user favorites in a list page.
    """
    favorites = Favorite.objects.filter(user=request.user).select_related('building')

    context = {
        'user': request.user,
        'favorites': favorites,
        'favorites_count': favorites.count(),
    }
    return render(request, 'accounts/favorites.html', context)


@login_required
def saved_routes_view(request):
    """
    View to display all saved routes for the current user.
    """
    saved_routes = SavedRoute.objects.filter(user=request.user).select_related('destination_building')

    context = {
        'user': request.user,
        'saved_routes': saved_routes,
        'saved_routes_count': saved_routes.count(),
    }
    return render(request, 'accounts/saved_routes.html', context)


@login_required
@require_http_methods(["POST"])
def save_route_api(request):
    """
    API endpoint to save a new route.
    """
    import json
    from django.utils import timezone

    try:
        data = json.loads(request.body)

        # Extract route data
        name = data.get('name', '').strip()
        origin_lat = data.get('origin_lat')
        origin_lng = data.get('origin_lng')
        origin_name = data.get('origin_name', 'My Location').strip()
        destination_lat = data.get('destination_lat')
        destination_lng = data.get('destination_lng')
        destination_name = data.get('destination_name', '').strip()
        destination_building_id = data.get('destination_building_id')
        distance_text = data.get('distance_text', '')
        duration_text = data.get('duration_text', '')
        distance_value = data.get('distance_value', 0)
        duration_value = data.get('duration_value', 0)

        # Validate required fields
        if not all([name, origin_lat, origin_lng, destination_lat, destination_lng, destination_name]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)

        # Get destination building if provided
        destination_building = None
        if destination_building_id:
            try:
                destination_building = Building.objects.get(id=destination_building_id)
            except Building.DoesNotExist:
                pass

        # Create the saved route
        saved_route = SavedRoute.objects.create(
            user=request.user,
            name=name,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            origin_name=origin_name,
            destination_lat=destination_lat,
            destination_lng=destination_lng,
            destination_name=destination_name,
            destination_building=destination_building,
            distance_text=distance_text,
            duration_text=duration_text,
            distance_value=distance_value,
            duration_value=duration_value,
            last_used=timezone.now()
        )

        return JsonResponse({
            'success': True,
            'message': f'Route "{name}" saved successfully',
            'route_id': saved_route.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def get_saved_routes_api(request):
    """
    API endpoint to get all saved routes for the current user.
    """
    saved_routes = SavedRoute.objects.filter(user=request.user).select_related('destination_building')

    results = []
    for route in saved_routes:
        results.append({
            'id': route.id,
            'name': route.name,
            'origin_lat': float(route.origin_lat),
            'origin_lng': float(route.origin_lng),
            'origin_name': route.origin_name,
            'destination_lat': float(route.destination_lat),
            'destination_lng': float(route.destination_lng),
            'destination_name': route.destination_name,
            'destination_display': route.get_destination_display(),
            'destination_building_id': route.destination_building.id if route.destination_building else None,
            'distance_text': route.distance_text,
            'duration_text': route.duration_text,
            'distance_value': route.distance_value,
            'duration_value': route.duration_value,
            'created_at': route.created_at.isoformat(),
            'last_used': route.last_used.isoformat() if route.last_used else None,
        })

    return JsonResponse({
        'success': True,
        'count': len(results),
        'routes': results
    })


@login_required
@require_http_methods(["POST"])
def load_saved_route_api(request):
    """
    API endpoint to load a saved route (updates last_used timestamp).
    """
    import json
    from django.utils import timezone

    try:
        data = json.loads(request.body)
        route_id = data.get('route_id')

        if not route_id:
            return JsonResponse({
                'success': False,
                'error': 'Route ID is required'
            }, status=400)

        # Get route and verify ownership
        try:
            route = SavedRoute.objects.get(id=route_id, user=request.user)
        except SavedRoute.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Route not found or you do not have permission'
            }, status=404)

        # Update last_used timestamp
        route.last_used = timezone.now()
        route.save()

        return JsonResponse({
            'success': True,
            'route': {
                'id': route.id,
                'name': route.name,
                'origin_lat': float(route.origin_lat),
                'origin_lng': float(route.origin_lng),
                'origin_name': route.origin_name,
                'destination_lat': float(route.destination_lat),
                'destination_lng': float(route.destination_lng),
                'destination_name': route.destination_name,
                'destination_building_id': route.destination_building.id if route.destination_building else None,
                'distance_text': route.distance_text,
                'duration_text': route.duration_text,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_saved_route_api(request):
    """
    API endpoint to delete a saved route.
    """
    import json

    try:
        data = json.loads(request.body)
        route_id = data.get('route_id')

        if not route_id:
            return JsonResponse({
                'success': False,
                'error': 'Route ID is required'
            }, status=400)

        # Get route and verify ownership
        try:
            route = SavedRoute.objects.get(id=route_id, user=request.user)
        except SavedRoute.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Route not found or you do not have permission'
            }, status=404)

        route_name = route.name
        route.delete()

        return JsonResponse({
            'success': True,
            'message': f'Route "{route_name}" deleted successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_alerts_api(request):
    """
    API endpoint for fetching active safety alerts.
    Returns all currently active alerts with optional filtering.
    """
    # Get optional query parameters
    alert_type = request.GET.get('alert_type')
    severity = request.GET.get('severity')
    bounds = request.GET.get('bounds')  # Format: "north,south,east,west"
    
    # Get all alerts that are currently active
    alerts = SafetyAlert.objects.filter(is_active=True).select_related('created_by')
    
    # Filter by alert type if provided
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    
    # Filter by severity if provided
    if severity:
        alerts = alerts.filter(severity=severity)
    
    # Filter by map bounds if provided (optional optimization)
    if bounds:
        try:
            north, south, east, west = map(float, bounds.split(','))
            alerts = alerts.filter(
                latitude__lte=north,
                latitude__gte=south,
                longitude__lte=east,
                longitude__gte=west
            )
        except (ValueError, TypeError):
            # Invalid bounds format, ignore it
            pass
    
    # Filter to only currently active alerts (based on dates)
    active_alerts = [alert for alert in alerts if alert.is_currently_active()]
    
    # Format results as JSON
    results = []
    for alert in active_alerts:
        alert_data = {
            'id': alert.id,
            'title': alert.title,
            'description': alert.description,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'location_type': alert.location_type,
            'is_active': alert.is_active,
            'created_at': alert.created_at.isoformat(),
            'updated_at': alert.updated_at.isoformat(),
            'icon_url': alert.get_icon_url(),
            'color': alert.get_color(),
        }
        
        # Add address if available
        if alert.address:
            alert_data['address'] = alert.address
        
        # Add coordinates if available (for backwards compatibility)
        if alert.latitude is not None and alert.longitude is not None:
            alert_data['latitude'] = float(alert.latitude)
            alert_data['longitude'] = float(alert.longitude)
        
        # Add location-specific data
        if alert.location_type == 'circle' and alert.radius:
            alert_data['radius'] = float(alert.radius)
        
        if alert.location_type == 'polygon':
            polygon_coords = alert.get_polygon_coordinates()
            if polygon_coords:
                alert_data['polygon_coordinates'] = polygon_coords
        
        # Add date information
        if alert.start_date:
            alert_data['start_date'] = alert.start_date.isoformat()
        if alert.end_date:
            alert_data['end_date'] = alert.end_date.isoformat()
        
        results.append(alert_data)
    
    return JsonResponse({
        'success': True,
        'count': len(results),
        'alerts': results
    })


def get_alert_detail_api(request, alert_id):
    """
    API endpoint to get detailed information about a single alert.
    """
    try:
        alert = SafetyAlert.objects.select_related('created_by').get(id=alert_id)
        
        alert_data = {
            'id': alert.id,
            'title': alert.title,
            'description': alert.description,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'location_type': alert.location_type,
            'latitude': float(alert.latitude),
            'longitude': float(alert.longitude),
            'is_active': alert.is_active,
            'created_at': alert.created_at.isoformat(),
            'updated_at': alert.updated_at.isoformat(),
            'icon_url': alert.get_icon_url(),
            'color': alert.get_color(),
        }
        
        if alert.location_type == 'circle' and alert.radius:
            alert_data['radius'] = float(alert.radius)
        
        if alert.location_type == 'polygon':
            polygon_coords = alert.get_polygon_coordinates()
            if polygon_coords:
                alert_data['polygon_coordinates'] = polygon_coords
        
        if alert.start_date:
            alert_data['start_date'] = alert.start_date.isoformat()
        if alert.end_date:
            alert_data['end_date'] = alert.end_date.isoformat()
        
        if alert.created_by:
            alert_data['created_by'] = {
                'id': alert.created_by.id,
                'email': alert.created_by.email,
                'full_name': alert.created_by.get_full_name()
            }
        
        return JsonResponse({
            'success': True,
            'alert': alert_data
        })
        
    except SafetyAlert.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Alert not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
