from functools import wraps
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from users.models import SalonAccount


def user_passes_test(test_func):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                print(request)
                return view_func(request, *args, **kwargs)

            return HttpResponseNotFound()
        return _wrapped_view
    return decorator



def manager_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    # print(function)
    actual_decorator = user_passes_test(
        lambda r: True if r.user.groups.filter(name='Manager').exists() else False
    )
    if function:
        # print(function)
        return actual_decorator(function)
    return actual_decorator



def salon_account_check(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def test(request):
        return  request.user.salonAcc == get_object_or_404(SalonAccount, website=request.META['HTTP_HOST'])

    actual_decorator = user_passes_test(test)
    if function:
        return actual_decorator(function)
    return actual_decorator



