from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'You need admin access for that.')
            return redirect('attendant_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
