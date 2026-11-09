from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    role = forms.ChoiceField(choices=[('buyer', 'Buyer / Tenant'), ('agent', 'Agent / Owner')])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'bio', 'avatar',
            'address', 'city', 'country', 'website',
            'facebook', 'twitter', 'instagram', 'linkedin', 'whatsapp',
        ]


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'filter-input'})
