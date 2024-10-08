from django.urls import path
from django.contrib import admin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app import views

urlpatterns = [
    # Home page (requires authentication)
    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.register_view, name='register'), 

    # JWT Token endpoints (default views provided by SimpleJWT)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Default JWT login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Custom JWT login endpoint
    path('api/jwt-login/', views.jwt_login, name='jwt_login'),

    # Admin interface
    path('admin/', admin.site.urls),
    
    # Main pages
    path('systemhealthcheck/system-health-check/', views.system_health_check, name='system_health_check'),
    path('systemhealthcheck/low_stock_items/', views.low_stock_items, name='low_stock_items'),
    path('systemhealthcheck/maintenance_repair_items/', views.maintenance_repair_items, name='maintenance_repair_items'),

    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/new/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/edit/', views.equipment_update, name='equipment_update'),
    path('equipment/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    path('equipment/assign-equipment-list/', views.assign_equipment_list, name='assign_equipment_list'),


    path('employee/', views.employee_list, name='employee_list'),
    path('employee/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employee/new/', views.employee_create, name='employee_create'),
    path('employee/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employee/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    path('admin-controls/', views.admin_controls, name='admin_controls'),
    path('toggle-superuser/<int:user_id>/', views.toggle_superuser_status, name='toggle_superuser_status'),

    path('error-logs/', views.error_logs, name='error_logs'),
    path('trigger-error/', views.trigger_error, name='trigger_error'),
]
