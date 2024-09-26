from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Equipment, Employee, ErrorLog
from .decorators import login_required, user_is_superuser
from .forms import AssignEquipmentForm, EquipmentForm, EmployeeForm, UserRegistrationForm
from datetime import datetime
from xhtml2pdf import pisa
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings

import logging

logger = logging.getLogger('django')

LOW_STOCK_THRESHOLD = 10

@api_view(['POST'])
def jwt_login(request):
    try:
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
    except Exception as e:
        
        logger.warning(f'Failed JWT authentication attempt for username: {username}.')
   
        ErrorLog.objects.create(
            user=request.user,  # Save the current user
            error_message=str(e),
            severity='error'  
        )
    return JsonResponse({'error': 'Invalid credentials'}, status=400)


@login_required
def home(request):
    return render(request, 'app/home.html', {'title': 'Home'})

def login_view(request):
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
    logout(request)
    logger.info('User logged out successfully.')
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            email = form.cleaned_data.get('email')
            if User.objects.filter(username=username).exists():
                logger.warning(f'Registration attempt with existing username: {username}.')
                return JsonResponse({'errors': {'username': [{'message': 'A user with this username already exists.'}]}}, status=400)
            elif User.objects.filter(email=email).exists():
                logger.warning(f'Registration attempt with existing email: {email}.')
                return JsonResponse({'errors': {'email': [{'message': 'A user with this email already exists.'}]}}, status=400)

            user = form.save(commit=False)
            user.username = username
            user.save()

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
            errors = {field: [{'message': error} for error in error_list] for field, error_list in form.errors.items()}
            return JsonResponse({'errors': errors}, status=400)

    form = UserRegistrationForm()
    return render(request, 'app/register.html', {'form': form})

@login_required
def system_health_check(request):
    try:
        low_stock_count = Equipment.objects.filter(stock__lt=LOW_STOCK_THRESHOLD).count()
        maintenance_count = Equipment.objects.filter(usage_status='maintenance').count()
        repair_count = Equipment.objects.filter(usage_status='in_repair').count()
        total_equipment = Equipment.objects.count()

        system_health = ((total_equipment - (low_stock_count + maintenance_count + repair_count)) / total_equipment) * 100 if total_equipment > 0 else 100

        context = {
            'low_stock_count': low_stock_count,
            'maintenance_count': maintenance_count,
            'repair_count': repair_count,
            'system_health': system_health,
        }
        return render(request, 'app/systemhealthcheck/system_health_check.html', context)
    except Exception as e:
        logger.error(f'Error checking system health: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        return render(request, 'app/systemhealthcheck/system_health_check.html', {'error': 'An error occurred while checking system health.'})


@login_required
def low_stock_items(request):
    try:
        low_stock_items = Equipment.objects.filter(stock__lt=LOW_STOCK_THRESHOLD)
        return render(request, 'app/systemhealthcheck/low_stock_items.html', {'low_stock_items': low_stock_items})
    except Exception as e:
        logger.error(f'Error retrieving low stock items: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        return render(request, 'app/systemhealthcheck/low_stock_items.html', {'error': 'An error occurred while retrieving low stock items.'})


@login_required
def maintenance_repair_items(request):
    try:
        maintenance_items = Equipment.objects.filter(usage_status='maintenance')
        repair_items = Equipment.objects.filter(usage_status='in_repair')
        return render(request, 'app/systemhealthcheck/maintenance_repair_items.html', {'maintenance_items': maintenance_items, 'repair_items': repair_items})
    except Exception as e:
        logger.error(f'Error retrieving maintenance and repair items: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        return render(request, 'app/systemhealthcheck/maintenance_repair_items.html', {'error': 'An error occurred while retrieving maintenance and repair items.'})


@login_required
def equipment_list(request):
    try:
        equipments = Equipment.objects.all()
        return render(request, 'app/equipment/equipment_list.html', {'equipments': equipments})
    except Exception as e:
        logger.error(f'Error retrieving equipment list: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        return render(request, 'app/equipment/equipment_list.html', {'error': 'An error occurred while retrieving the equipment list.'})


@login_required
def equipment_detail(request, pk):
    try:
        equipment = get_object_or_404(Equipment, pk=pk)
        return render(request, 'app/equipment/equipment_detail.html', {'equipment': equipment})
    except Exception as e:
        logger.error(f'Error retrieving equipment detail for ID {pk}: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        return render(request, 'app/equipment/equipment_detail.html', {'error': 'An error occurred while retrieving equipment details.'})


@login_required
def equipment_create(request):
    if request.method == "POST":
        try:
            form = EquipmentForm(request.POST)
            if form.is_valid():
                form.save()
                logger.info('New equipment created successfully.')
                messages.success(request, 'Equipment successfully created!')
                return redirect('equipment_list')
            else:
                logger.error(f'Failed to create equipment. Form errors: {form.errors}')
                messages.error(request, 'Failed to create equipment. Please check the form for errors.')
        except Exception as e:
            logger.error(f'Error creating equipment: {str(e)}')
            ErrorLog.objects.create(
                user=request.user,
                error_message=str(e),
                severity='error'
            )
            messages.error(request, 'An error occurred while creating equipment. Please try again.')

    else:
        form = EquipmentForm()
    return render(request, 'app/equipment/equipment_form.html', {'form': form})


@login_required
def equipment_update(request, pk):
    try:
        equipment = get_object_or_404(Equipment, pk=pk)
        if request.method == "POST":
            form = EquipmentForm(request.POST, instance=equipment)
            if form.is_valid():
                form.save()
                logger.info(f'Equipment {pk} updated successfully.')
                messages.success(request, 'Equipment successfully updated!')
                return redirect('equipment_list')
            else:
                logger.error(f'Failed to update equipment {pk}. Form errors: {form.errors}')
                messages.error(request, 'Failed to update equipment. Please check the form for errors.')
        else:
            form = EquipmentForm(instance=equipment)
        return render(request, 'app/equipment/equipment_form.html', {'form': form})

    except Exception as e:
        logger.error(f'Error updating equipment {pk}: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while updating equipment. Please try again.')
        return redirect('equipment_list')


@user_is_superuser
@login_required
def equipment_delete(request, pk):
    try:
        equipment = get_object_or_404(Equipment, pk=pk)
        if request.method == "POST":
            equipment.delete()
            logger.info(f'Equipment {pk} deleted successfully.')
            messages.success(request, 'Equipment successfully deleted!')
            return redirect('equipment_list')
        return render(request, 'app/equipment/equipment_confirm_delete.html', {'equipment': equipment})
    except Exception as e:
        logger.error(f'Error deleting equipment {pk}: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while deleting equipment. Please try again.')
        return redirect('equipment_list')
    
@login_required
def assign_equipment_list(request):
    try:
        if request.method == 'POST':
            form = AssignEquipmentForm(request.POST)
            if form.is_valid():
                employee = form.cleaned_data['employee']
                equipment = form.cleaned_data['equipment']

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
                logger.error(f'Failed to assign equipment. Form errors: {form.errors}')
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

    except Exception as e:
        logger.error(f'Error in assigning equipment: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while assigning equipment. Please try again.')
        return redirect('assign_equipment_list')


@login_required
def employee_list(request):
    try:
        employees = Employee.objects.all()
        return render(request, 'app/employee/employee_list.html', {'employees': employees})
    except Exception as e:
        logger.error(f'Error retrieving employee list: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while retrieving the employee list.')
        return redirect('employee_list')


@login_required
def employee_detail(request, pk):
    try:
        employee = get_object_or_404(Employee, pk=pk)
        return render(request, 'app/employee/employee_detail.html', {'employee': employee})
    except Exception as e:
        logger.error(f'Error retrieving employee detail for ID {pk}: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while retrieving employee details.')
        return redirect('employee_list')


@login_required
def employee_create(request):
    if request.method == "POST":
        try:
            form = EmployeeForm(request.POST)
            if form.is_valid():
                form.save()
                logger.info('New employee created successfully.')
                messages.success(request, 'Employee successfully created!')
                return redirect('employee_list')
            else:
                logger.error(f'Failed to create employee. Form errors: {form.errors}')
                messages.error(request, 'Failed to create employee. Please check the form for errors.')
        except Exception as e:
            logger.error(f'Error creating employee: {str(e)}')
            ErrorLog.objects.create(
                user=request.user,
                error_message=str(e),
                severity='error'
            )
            messages.error(request, 'An error occurred while creating the employee. Please try again.')
    
    else:
        form = EmployeeForm()
    return render(request, 'app/employee/employee_form.html', {'form': form})


@login_required
def employee_update(request, pk):
    try:
        employee = get_object_or_404(Employee, pk=pk)
        if request.method == "POST":
            form = EmployeeForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                logger.info(f'Employee {pk} updated successfully.')
                messages.success(request, 'Employee successfully updated!')
                return redirect('employee_list')
            else:
                logger.error(f'Failed to update employee {pk}. Form errors: {form.errors}')
                messages.error(request, 'Failed to update employee. Please check the form for errors.')
        else:
            form = EmployeeForm(instance=employee)
        return render(request, 'app/employee/employee_form.html', {'form': form})

    except Exception as e:
        logger.error(f'Error updating employee {pk}: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while updating the employee. Please try again.')
        return redirect('employee_list')

@user_is_superuser
@login_required
def employee_delete(request, pk):
    try:
        employee = get_object_or_404(Employee, pk=pk)
        if request.method == "POST":
            employee.delete()
            logger.info(f'Employee {pk} deleted successfully.')
            messages.success(request, 'Employee successfully deleted!')
            return redirect('employee_list')
        return render(request, 'app/employee/employee_confirm_delete.html', {'employee': employee})
    except Exception as e:
        logger.error(f'Error deleting employee {pk}: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while deleting the employee. Please try again.')
        return redirect('employee_list')

@api_view(['POST'])
@login_required
def get_jwt_token(request):
    refresh = RefreshToken.for_user(request.user)
    return JsonResponse({
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })

@api_view(['GET'])
@login_required
def protected_view(request):
    return JsonResponse({'message': 'You have accessed a protected view!'})

@login_required
def trigger_error(request):
    try:
        # Deliberate error
        result = 1 / 0
    except Exception as e:
        # Log the error to the console
        logger.error('Deliberate error occurred: %s', str(e))

        # Save the error in the database
        ErrorLog.objects.create(
            user=request.user,  # Save the current user
            error_message=str(e),
            severity='error' 
        )

        return HttpResponse('An error occurred and was logged.', status=500)

    return HttpResponse('No error occurred.', status=200)

@user_is_superuser
@login_required
def toggle_superuser_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        if user.is_superuser:
            user.is_superuser = False
            messages.success(request, f"{user.username} is no longer an admin.")
            action = 'removed'
        else:
            user.is_superuser = True
            messages.success(request, f"{user.username} is now an admin.")
            action = 'granted'

        user.save()
        logger.info(f"Superuser status for user {user.username} has been updated.")

        # Prepare the email content
        subject = f"Administrative Privileges {action.capitalize()}"
        message = f"""
        Dear {user.username},

        We would like to inform you that your administrative privileges on {get_current_site(request).domain} have been {action}.
        As of now, your account has been updated to reflect this change.

        Please note that this decision was made based on the current requirements of the system and organizational needs. 
        If you have any questions regarding this action or believe it was made in error, feel free to reach out to our support team.

        We value your contributions and hope you continue to find success in your role within the organization.

        Best regards,
        The {get_current_site(request).domain} Team
        """
        
        email_message = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        try:
            email_message.send()
            logger.info(f"Email sent to {user.email} regarding admin status change.")
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}. Error: {e}")
        
    except Exception as e:
        logger.error(f"Error toggling superuser status for user ID {user_id}: {str(e)}")
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while updating superuser status. Please try again.')

    return redirect('admin_console')


@user_is_superuser
@login_required
def admin_controls(request):
    try:
        users = User.objects.all()
        return render(request, 'app/admin/controls_admin.html', {'users': users})
    except Exception as e:
        logger.error(f'Error retrieving admin controls: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while retrieving admin controls.')
        return redirect('admin_console')


# Error Logging Page
@login_required
@user_is_superuser
def error_logs(request):
    try:
        logs = ErrorLog.objects.all().order_by('-timestamp')
        return render(request, 'app/admin/error_logs_list.html', {'logs': logs})
    except Exception as e:
        logger.error(f'Error retrieving error logs: {str(e)}')
        ErrorLog.objects.create(
            user=request.user,
            error_message=str(e),
            severity='error'
        )
        messages.error(request, 'An error occurred while retrieving error logs.')
        return redirect('admin_console')
