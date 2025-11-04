from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('map/', views.map_view, name='map'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('saved-routes/', views.saved_routes_view, name='saved_routes'),
    path('api/buildings/search/', views.building_search_api, name='building_search_api'),
    path('api/favorites/toggle/', views.toggle_favorite_api, name='toggle_favorite'),
    path('api/favorites/', views.user_favorites_api, name='user_favorites'),
    path('api/favorites/check/', views.check_favorite_api, name='check_favorite'),
    path('api/favorites/rename/', views.rename_favorite_api, name='rename_favorite'),
    path('api/favorites/delete/', views.delete_favorite_api, name='delete_favorite'),
    path('api/routes/save/', views.save_route_api, name='save_route'),
    path('api/routes/', views.get_saved_routes_api, name='get_saved_routes'),
    path('api/routes/load/', views.load_saved_route_api, name='load_saved_route'),
    path('api/routes/delete/', views.delete_saved_route_api, name='delete_saved_route'),
]
