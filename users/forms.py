from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'profile_picture', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))
