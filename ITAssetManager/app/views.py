from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Equipment, Employee
from .forms import AssignEquipmentForm, EquipmentForm, EmployeeForm
from .decorators import login_required

LOW_STOCK_THRESHOLD = 5  # Define what equates to a low stock count

@login_required
def home(request):
    return render(request, 'app/home.html', {'title': 'Home'})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'app/login.html', {'title': 'Login', 'error': 'Invalid credentials'})
    return render(request, 'app/login.html', {'title': 'Login'})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def system_health_check(request):
    low_stock_count = Equipment.objects.filter(stock__lt=LOW_STOCK_THRESHOLD).count()
    maintenance_count = Equipment.objects.filter(usage_status='maintenance').count()
    repair_count = Equipment.objects.filter(usage_status='in_repair').count()
    total_equipment = Equipment.objects.count()

    # Calculate system health as a percentage
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
    low_stock_items = Equipment.objects.filter(stock__lt=LOW_STOCK_THRESHOLD)
    context = {
        'low_stock_items': low_stock_items,
    }
    return render(request, 'low_stock_items.html', context)

@login_required
def maintenance_repair_items(request):
    maintenance_items = Equipment.objects.filter(usage_status='maintenance')
    repair_items = Equipment.objects.filter(usage_status='in_repair')
    context = {
        'maintenance_items': maintenance_items,
        'repair_items': repair_items,
    }
    return render(request, 'maintenance_repair_items.html', context)


@login_required
def equipment_list(request):
    equipments = Equipment.objects.all()
    return render(request, 'app/equipment/equipment_list.html', {'equipments': equipments})

@login_required
def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    return render(request, 'app/equipment/equipment_detail.html', {'equipment': equipment})

@login_required
def equipment_create(request):
    if request.method == "POST":
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'app/equipment/equipment_form.html', {'form': form})

@login_required
def equipment_update(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'app/equipment/equipment_form.html', {'form': form})

@login_required
def equipment_delete(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        equipment.delete()
        return redirect('equipment_list')
    return render(request, 'app/equipment/equipment_confirm_delete.html', {'equipment': equipment})

@login_required
def assign_equipment_list(request):
    if request.method == 'POST':
        form = AssignEquipmentForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            equipment = form.cleaned_data['equipment']
            employee.equipment.add(equipment)
            return redirect('assign_equipment_list')  
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
    employees = Employee.objects.all()
    return render(request, 'app/employee/employee_list.html', {'employees': employees})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'app/employee/employee_detail.html', {'employee': employee})

@login_required
def employee_create(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'app/employee/employee_form.html', {'form': form})

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'app/employee/employee_form.html', {'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        return redirect('employee_list')
    return render(request, 'app/employee/employee_confirm_delete.html', {'employee': employee})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return JsonResponse({'message': 'You have access to this protected view.'})

@api_view(['POST'])
def jwt_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return JsonResponse({'error': 'Invalid credentials'}, status=400)
