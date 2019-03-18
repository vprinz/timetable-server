from django import forms
from django.contrib.auth import password_validation

from .models import User


class BaseUserValidationForm(forms.Form):
    password = forms.CharField(
        label=('Пароль'),
        strip=False,
        widget=forms.PasswordInput,
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': ''}))

    def clean_password(self):
        password = self.cleaned_data.get("password")
        password_validation.validate_password(password)
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Адрес электронной почты уже существует')
        return email


class RegistrationForm(BaseUserValidationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=60)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def save(self):
        if not User.objects.filter(email=self.cleaned_data.get('email')).exists():
            data = {
                'email': self.cleaned_data.pop('email'),
                'password': self.cleaned_data.pop('password'),
                'last_name': self.cleaned_data.get('last_name'),
                'first_name': self.cleaned_data.get('first_name'),
            }
            user = User.objects.create_user(**data)
        else:
            user = User.objects.filter(email=self.cleaned_data.get('email'))

        user.save()
        return user
