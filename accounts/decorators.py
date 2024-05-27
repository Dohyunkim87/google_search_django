# accounts/decorators.py
from django.http import HttpResponse
from django.shortcuts import redirect

def login_required(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # 로그인 페이지로 리디렉션
        return function(request, *args, **kwargs)
    return wrapper