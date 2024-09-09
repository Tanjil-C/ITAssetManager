from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import RefreshToken

@permission_classes([IsAuthenticated])
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
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

@permission_classes([IsAuthenticated])
def item_management(request):
    return render(request, 'app/item_management.html', {'title': 'Item Management'})    


@permission_classes([IsAuthenticated])
def system_health_check(request):
    return render(request, 'app/system_health_check.html', {'title': 'System Health Check'})    


@permission_classes([IsAuthenticated])
def equipment_ordering(request):
    return render(request, 'app/equipment_ordering.html', {'title': 'Equipment Ordering'})    



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


