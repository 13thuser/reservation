from functools import wraps
from rest_framework.exceptions import ValidationError


def api_exception_handler(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            msg = getattr(e, 'messages') if hasattr(e, 'messages') else str(e)
            raise ValidationError({'errors': msg})

    return wrapper
