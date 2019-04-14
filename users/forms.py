from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm

from .models import User


class RegistrationForm(forms.Form):
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


class AuthenticationForm(BaseAuthenticationForm):
    def confirm_login_allowed(self, user):
        # if user.is_staff:
        #     raise forms.ValidationError(self.error_messages['inactive'], code='inactive')
        super(AuthenticationForm, self).confirm_login_allowed(user)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if not User.objects.filter(email=username).exists():
            raise forms.ValidationError('Учетная запись не связана с этим адресом электронной почты.')
        return username

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if User.objects.filter(email=username).exists() and \
                not authenticate(username=username, password=password):
            raise forms.ValidationError('Неверный пароль. Обратите внимание, что пароли чувствительны к регистру.')
        return password
