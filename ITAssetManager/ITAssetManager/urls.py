from django.urls import path
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app import views

urlpatterns = [
    # Home page (requires authentication)
    path('', views.home, name='home'),

    # Login page (public, users can access without being logged in)
    path('login/', views.login_view, name='login'),

    # JWT Token endpoints (default views provided by SimpleJWT)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Default JWT login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Admin interface
    path('admin/', admin.site.urls),
]
