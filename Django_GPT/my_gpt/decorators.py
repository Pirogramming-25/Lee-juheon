from functools import wraps
from urllib.parse import urlencode

from django.shortcuts import redirect


def model_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        login_url = "/accounts/login/"
        query = urlencode(
            {
                "next": request.path,
                "required": "1",
            }
        )
        return redirect(f"{login_url}?{query}")

    return wrapper