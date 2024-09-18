from django.http import HttpResponse
from django.shortcuts import redirect

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def user_is_superuser(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            # Return a 404 with custom message
            return HttpResponse('404 Not Authorized', status=404)
        return view_func(request, *args, **kwargs)
    return _wrapped_view