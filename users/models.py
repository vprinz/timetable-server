from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from university.models import Group


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


class User(PermissionsMixin, AbstractBaseUser):
    USERNAME_FIELD = 'email'

    objects = UserManager()

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    email = models.CharField(max_length=120, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)

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
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name


class Device(models.Model):
    iOS = 'iOS'
    ANDROID = 'Android'

    PLATFORMS = (
        (iOS, 'iOS'),
        (ANDROID, 'Android')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, choices=PLATFORMS)

    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'

    def __str__(self):
        return f'{self.user} | {self.platform}'
