from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django.contrib.auth import authenticate

class CustomSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'profile_picture', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))

    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                # Check if email exists in the database
                from .models import User
                if User.objects.filter(email=email).exists():
                    self.add_error('password', 'Incorrect password.')
                else:
                    self.add_error('username', 'No user found with this email.')
        return cleaned_data