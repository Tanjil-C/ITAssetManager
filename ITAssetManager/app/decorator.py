
# app/decorators.py
from django.shortcuts import redirect
from functools import wraps
from rest_framework_simplejwt.tokens import AccessToken

def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not AccessToken(token.split(' ')[1]).check_token():
            return redirect('login')  # Make sure 'login' matches the name in urls.py
        return view_func(request, *args, **kwargs)
    return _wrapped_view
