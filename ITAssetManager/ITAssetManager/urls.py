from django.urls import path
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app import views

urlpatterns = [
# Home page (requires authentication)
path('', views.home, name='home'),

# Login page (public, users can access without being logged in)
path('login/', views.login_view, name='login'),

# Logout page
path('logout/', views.logout_view, name='logout'),

# JWT Token endpoints (default views provided by SimpleJWT)
path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Default JWT login
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

# Custom JWT login endpoint
path('api/jwt-login/', views.jwt_login, name='jwt_login'),


# Admin interface
path('admin/', admin.site.urls),

# Main pages
path('item-management', views.item_management, name='item_management'),
path('system-health-check', views.system_health_check, name='system_health_check'),
path('equipment-ordering', views.equipment_ordering, name='equipment_ordering'),
]
   