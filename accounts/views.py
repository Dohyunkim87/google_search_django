from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # 로그인 후 리디렉션할 URL
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'template/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')  # 로그아웃 후 리디렉션할 URL

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')  # 회원가입 후 리디렉션할 URL
    else:
        form = UserCreationForm()
    return render(request, 'template/register.html', {'form': form})


def home_before_login(request):
    return render(request, 'template/home.html')

@login_required
def home_after_login(request):
    return redirect('index')  # 로그인 후에는 검색 앱의 홈으로 리디렉션

def home_view(request):
    if request.user.is_authenticated:
        return home_after_login(request)
    else:
        return home_before_login(request)