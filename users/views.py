from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import CustomSignupForm, CustomLoginForm
from .models import User

def register_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful.")
            return redirect('users:login')  # ✅ this is correct
    else:
        form = CustomSignupForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('article:article_list')   # or redirect by role
        else:
            messages.error(request, "Invalid credentials.")
    form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})
