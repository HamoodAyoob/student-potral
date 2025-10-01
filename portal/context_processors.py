def user_type(request):
    if request.user.is_authenticated:
        return {
            'is_student': hasattr(request.user, 'student'),
            'is_teacher': hasattr(request.user, 'teacher'),
        }
    return {
        'is_student': False,
        'is_teacher': False,
    }