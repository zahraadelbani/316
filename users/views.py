from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import CustomSignupForm, CustomLoginForm, EditProfileForm
from .models import User

def register_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful.")
            return redirect('users:login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomSignupForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if request.user.is_superuser:
                return redirect('users:list_users')
            return redirect('article:article_list')
    else:
        form = CustomLoginForm()
    return render(request, 'users/login.html', {'form': form})



@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@login_required
def change_user_role(request, user_id):
    if request.user.get_role != "admin":
        return HttpResponseForbidden("Only admins can change user roles.")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        new_role = request.POST.get("role")
        if new_role in dict(User.ROLE_CHOICES).keys():
            user.role = new_role
            user.save()
            messages.success(request, "User role updated.")
        return redirect('users:list_users')  # Update this with your actual user list view name

    return render(request, "users/change_user_role.html", {"user": user})

@login_required
def list_users(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")

    users = User.objects.all().order_by("-date_joined")
    return render(request, "users/list_users.html", {"users": users})



@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('users:profile')  # <- Redirect to profile page
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})