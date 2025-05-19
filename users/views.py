from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
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
            return redirect('users:login')  # Redirect to login after registration
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
            # 🔁 Redirect based on role
            if user.is_superuser:
                return redirect('users:list_users')
            else:
                return redirect('article:article_list')
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