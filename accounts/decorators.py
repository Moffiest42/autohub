from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        if request.user.role != 'ADMIN':
            raise PermissionDenied   # 403 даже при прямом URL или ручном POST
        return view_func(request, *args, **kwargs)
    return wrapper