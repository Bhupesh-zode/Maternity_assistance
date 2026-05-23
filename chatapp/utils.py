from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages

from mainapp.models import mainModel


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
