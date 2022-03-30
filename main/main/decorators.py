from functools import wraps
from pathlib import Path
import logging, os

from django.conf import settings

logs_path = os.path.join(Path(settings.BASE_DIR).parents[0], 'logs')

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(os.path.join(logs_path, 'customers.log'))

file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)



logger.addHandler(file_handler)



def log_exception(func):
    """
    Decorator for log exceptions
    """

    def decorator(func):
        @wraps(func)
        def _wrapped_func(request, *args, **kwargs):
            try:
                func()
            except Exception as e:
                pass
            return _wrapped_func
    return decorator