from functools import wraps
from urllib.parse import urlencode

from django.http import JsonResponse
from django.shortcuts import redirect


def model_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        if request.method == "POST":
            return JsonResponse(
                {"error": "로그인이 만료되었습니다. 다시 로그인해주세요."},
                status=401,
            )

        login_url = "/accounts/login/"
        query = urlencode(
            {
                "next": request.path,
                "required": "1",
            }
        )
        return redirect(f"{login_url}?{query}")

    return wrapper