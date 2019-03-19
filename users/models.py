from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Необходимо указать email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_staff(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    objects = UserManager()

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    email = models.CharField(max_length=120, unique=True)

    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Указывает, может ли пользователь войти на этот сайт как администратор.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Указывает, следует ли считать этого пользователя активным. Отмените выбор вместо удаления'
                  'учетных записей.'
    )

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name
