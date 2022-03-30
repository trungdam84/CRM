from .models import ExcetionLogs
from customers.models import SalonAccount
from django.utils import timezone
import traceback, inspect, random, string
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

# def decorator(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         if not test_func(request.user):
#             messages.add_message(request, messages.ERROR, message)
#         if test_func(request.user):
#             return view_func(request, *args, **kwargs)
#         path = request.build_absolute_uri()
#         resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
#         # If the login url is the same scheme and net location then just
#         # use the path as the "next" url.
#         login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
#         current_scheme, current_netloc = urlparse(path)[:2]
#         if ((not login_scheme or login_scheme == current_scheme) and
#                 (not login_netloc or login_netloc == current_netloc)):
#             path = request.get_full_path()
#         return redirect_to_login(
#             path, resolved_login_url, redirect_field_name)
#     return _wrapped_view
# return decorator
def front_end_exception_log(view_func):

    def wrap(request, *args, **kwargs):
        
        try:
            
            return view_func(request, *args, **kwargs)
        except Exception as e:
            salonAcc = get_object_or_404(SalonAccount, website=request.META['HTTP_HOST'])
            letters = string.digits
            error_code = ''.join(random.choice(letters) for i in range(10))
            ExcetionLogs.objects.create(module=(f'{view_func.__name__}'), dateTime=timezone.now(), exception=f'{e} {"".join(traceback.format_tb(e.__traceback__))}', error_code=error_code)
            context ={
                'error_code':error_code,
                'salonAcc':salonAcc
            }
            return render(request, 'customers/error.html', context)      
    return wrap
