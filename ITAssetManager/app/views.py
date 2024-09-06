from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from app.decorator import jwt_required

@permission_classes([IsAuthenticated])
def home(request):
    return render(request, 'app/home.html', {'title': 'Home'})

def login_view(request):
    return render(request, 'app/login.html', {'title': 'Login'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return JsonResponse({'message': 'You have access to this protected view.'})