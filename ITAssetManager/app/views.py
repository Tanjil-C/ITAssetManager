from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Equipment, Employee
from .forms import AssignEquipmentForm, EquipmentForm, EmployeeForm
from .decorators import login_required, user_is_superuser
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import UserRegistrationForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

import logging

logger = logging.getLogger('django')

LOW_STOCK_THRESHOLD = 10

@login_required
def home(request):
    return render(request, 'app/home.html', {'title': 'Home'})

def login_view(request):
    # Handle login for users
    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f'User {username} logged in successfully.')
            return redirect('home')
        else:
            logger.warning(f'Failed login attempt for username: {username}.')
            return render(request, 'app/login.html', {'title': 'Login', 'error': 'Invalid credentials'})
    return render(request, 'app/login.html', {'title': 'Login'})

def logout_view(request):
    # Log out the current user
    logout(request)
    logger.info('User logged out successfully.')
    return redirect('login')

def register_view(request):
    # Handle user registration
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            email = form.cleaned_data.get('email')

            # Check for existing users
            if User.objects.filter(username=username).exists():
                logger.warning(f'Registration attempt with existing username: {username}.')
                return JsonResponse({'errors': {'username': [{'message': 'A user with this username already exists.'}]}}, status=400)
            elif User.objects.filter(email=email).exists():
                logger.warning(f'Registration attempt with existing email: {email}.')
                return JsonResponse({'errors': {'email': [{'message': 'A user with this email already exists.'}]}}, status=400)

            user = form.save(commit=False)
            user.username = username
            user.save()

            # Send a welcome email to the new user
            subject = 'Welcome to Our Site!'
            message = render_to_string('email/welcome_email.html', {
                'user': user,
                'domain': get_current_site(request).domain,
            })
            plain_message = strip_tags(message)
            email_message = EmailMessage(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])

            try:
                email_message.send()
                logger.info(f'Welcome email sent to {email}.')
            except Exception as e:
                logger.error(f'Failed to send email to {email}. Error: {e}')

            return JsonResponse({'success': True})
        else:
            errors = {}
            for field, error_list in form.errors.items():
                if field == '__all__':
                    errors[field] = [{'message': error} for error in error_list]
                else:
                    errors[field] = [{'message': error} for error in error_list]

            return JsonResponse({'errors': errors}, status=400)

    form = UserRegistrationForm()
    return render(request, 'app/register.html', {'form': form})

@login_required
def system_health_check(request):
    # Check and return the system health metrics
    low_stock_count = Equipment.objects.filter(stock__lt=LOW_STOCK_THRESHOLD).count()
    maintenance_count = Equipment.objects.filter(usage_status='maintenance').count()
    repair_count = Equipment.objects.filter(usage_status='in_repair').count()
    total_equipment = Equipment.objects.count()

    if total_equipment > 0:
        system_health = ((total_equipment - (low_stock_count + maintenance_count + repair_count)) / total_equipment) * 100
    else:
        system_health = 100

    context = {
        'low_stock_count': low_stock_count,
        'maintenance_count': maintenance_count,
        'repair_count': repair_count,
        'system_health': system_health,
    }
    return render(request, 'app/systemhealthcheck/system_health_check.html', context)

@login_required
def low_stock_items(request):
    # Display items with stock below the threshold
    low_stock_items = Equipment.objects.filter(stock__lt=LOW_STOCK_THRESHOLD)
    context = {
        'low_stock_items': low_stock_items,
    }
    return render(request, 'app/systemhealthcheck/low_stock_items.html', context)

@login_required
def maintenance_repair_items(request):
    # Display items in maintenance or repair
    maintenance_items = Equipment.objects.filter(usage_status='maintenance')
    repair_items = Equipment.objects.filter(usage_status='in_repair')
    context = {
        'maintenance_items': maintenance_items,
        'repair_items': repair_items,
    }
    return render(request, 'app/systemhealthcheck/maintenance_repair_items.html', context)

@login_required
def equipment_list(request):
    # List all equipment
    equipments = Equipment.objects.all()
    return render(request, 'app/equipment/equipment_list.html', {'equipments': equipments})

@login_required
def equipment_detail(request, pk):
    # Display details of a specific equipment
    equipment = get_object_or_404(Equipment, pk=pk)
    return render(request, 'app/equipment/equipment_detail.html', {'equipment': equipment})

@user_is_superuser
@login_required
def equipment_create(request):
    # Handle creation of new equipment
    if request.method == "POST":
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info('New equipment created successfully.')
            messages.success(request, 'Equipment successfully created!')
            return redirect('equipment_list')
        else:
            logger.error('Failed to create equipment. Form errors: {}'.format(form.errors))
            messages.error(request, 'Failed to create equipment. Please check the form for errors.')
    else:
        form = EquipmentForm()
    return render(request, 'app/equipment/equipment_form.html', {'form': form})

@user_is_superuser
@login_required
def equipment_update(request, pk):
    # Handle updating existing equipment
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            logger.info(f'Equipment {pk} updated successfully.')
            messages.success(request, 'Equipment successfully updated!')
            return redirect('equipment_list')
        else:
            logger.error('Failed to update equipment. Form errors: {}'.format(form.errors))
            messages.error(request, 'Failed to update equipment. Please check the form for errors.')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'app/equipment/equipment_form.html', {'form': form})

@user_is_superuser
@login_required
def equipment_delete(request, pk):
    # Handle deletion of equipment
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        equipment.delete()
        logger.info(f'Equipment {pk} deleted successfully.')
        messages.success(request, 'Equipment successfully deleted!')
        return redirect('equipment_list')
    return render(request, 'app/equipment/equipment_confirm_delete.html', {'equipment': equipment})

@user_is_superuser
@login_required
def assign_equipment_list(request):
    # Handle assignment of equipment to employees
    if request.method == 'POST':
        form = AssignEquipmentForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            equipment = form.cleaned_data['equipment']
            
            # Check if there is stock available before assigning
            if equipment.stock > 0:
                employee.equipment.add(equipment)
                equipment.stock -= 1
                equipment.save()
                logger.info(f'Equipment {equipment.id} assigned to employee {employee.id}.')
                messages.success(request, 'Equipment successfully assigned to employee!')
            else:
                logger.warning(f'Attempt to assign equipment {equipment.id} with no stock.')
                messages.error(request, 'No stock available for this equipment.')
            
            return redirect('assign_equipment_list')
        else:
            logger.error('Failed to assign equipment. Form errors: {}'.format(form.errors))
            messages.error(request, 'Failed to assign equipment. Please check the form for errors.')
    else:
        form = AssignEquipmentForm()
    
    employees = Employee.objects.all()
    equipment = Equipment.objects.all()
    
    context = {
        'form': form,
        'employees': employees,
        'equipment': equipment
    }
    
    return render(request, 'app/equipment/assign_equipment_list.html', context)

@login_required
def employee_list(request):
    # List all employees
    employees = Employee.objects.all()
    return render(request, 'app/employee/employee_list.html', {'employees': employees})

@login_required
def employee_detail(request, pk):
    # Display details of a specific employee
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'app/employee/employee_detail.html', {'employee': employee})

@user_is_superuser
@login_required
def employee_create(request):
    # Handle creation of a new employee
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info('New employee created successfully.')
            messages.success(request, 'Employee successfully created!')
            return redirect('employee_list')
        else:
            logger.error('Failed to create employee. Form errors: {}'.format(form.errors))
            messages.error(request, 'Failed to create employee. Please check the form for errors.')
    else:
        form = EmployeeForm()
    return render(request, 'app/employee/employee_form.html', {'form': form})

@user_is_superuser
@login_required
def employee_update(request, pk):
    # Handle updating an existing employee
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            logger.info(f'Employee {pk} updated successfully.')
            messages.success(request, 'Employee successfully updated!')
            return redirect('employee_list')
        else:
            logger.error('Failed to update employee. Form errors: {}'.format(form.errors))
            messages.error(request, 'Failed to update employee. Please check the form for errors.')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'app/employee/employee_form.html', {'form': form})

@user_is_superuser
@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        logger.info(f'Employee {pk} deleted successfully.')
        messages.success(request, 'Employee successfully deleted!')
        return redirect('employee_list')
    return render(request, 'app/employee/employee_confirm_delete.html', {'employee': employee})

@api_view(['GET'])
@login_required
def protected_view(request):
    # Example of a protected API view that requires authentication
    logger.info('Access to protected view granted.')
    return JsonResponse({'message': 'You have access to this protected view.'})



@api_view(['POST'])
def jwt_login(request):
    # Handle JWT login and return tokens
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        logger.info(f'User {username} successfully authenticated with JWT.')
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    logger.warning(f'Failed JWT authentication attempt for username: {username}.')
    return JsonResponse({'error': 'Invalid credentials'}, status=400)


def trigger_error(request):
    try:
        # Deliberate error
        result = 1 / 0
    except Exception as e:
        # Log the error
        logger.error('Deliberate error occurred: %s', str(e))
        return HttpResponse('An error occurred and was logged.', status=500)

    return HttpResponse('No error occurred.', status=200)

@user_is_superuser
def admin_console(request):
    users = User.objects.all()
    return render(request, 'app/admin/admin_console.html', {'users': users})

@user_is_superuser
@user_passes_test(lambda u: u.is_superuser)
def toggle_superuser_status(request, user_id):
    user = User.objects.get(id=user_id)
    if user.is_superuser:
        user.is_superuser = False
        messages.success(request, f"{user.username} is no longer an admin.")
    else:
        user.is_superuser = True
        messages.success(request, f"{user.username} is now an admin.")
    user.save()
    logger.info(f"Superuser status for user {user.username} has been updated.")
    return redirect('admin_console')