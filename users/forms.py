from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.utils.translation import ugettext_lazy as _

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
    email = forms.EmailField(label=_("Email"), max_length=75)
    message_incorrect_password = _("Адрес электронной почты или пароль введен неверно.")
    message_inactive = _("Этот аккаунт неактивен.")

    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request, *args, **kwargs)
        del self.fields['username']
        self.fields.keyOrder = ['email', 'password']

    def confirm_login_allowed(self, user):
        super(AuthenticationForm, self).confirm_login_allowed(user)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if (self.user_cache is None):
                raise forms.ValidationError(self.message_incorrect_password)
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.message_inactive)
        return self.cleaned_data
