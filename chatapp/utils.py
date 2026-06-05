import os

from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages

from mainapp.models import mainModel

ALLOWED_SUPPORT_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.doc', '.docx',
}
MAX_SUPPORT_FILE_SIZE = 10 * 1024 * 1024


def validate_support_attachment(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_SUPPORT_EXTENSIONS:
        return (
            'Unsupported file type. Allowed: images (JPG, PNG, GIF, WEBP) '
            'and reports (PDF, DOC, DOCX).'
        )
    if uploaded_file.size > MAX_SUPPORT_FILE_SIZE:
        return 'File is too large. Maximum size is 10 MB.'
    return None


def get_logged_in_user(request):
    sno = request.session.get('sno')
    if not sno:
        return None
    try:
        return mainModel.objects.get(sno=sno)
    except mainModel.DoesNotExist:
        return None


def user_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not get_logged_in_user(request):
            messages.info(request, 'Please log in to use the pregnancy assistant.')
            return redirect('userlogin')
        return view_func(request, *args, **kwargs)

    return wrapper


def is_admin_logged_in(request):
    return request.session.get('admin_logged_in') is True


def admin_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_admin_logged_in(request):
            messages.info(request, 'Please log in as admin to continue.')
            return redirect('adminlogin')
        return view_func(request, *args, **kwargs)

    return wrapper
