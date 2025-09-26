from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def student_required(function):
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'student'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

def teacher_required(function):
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'teacher'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap