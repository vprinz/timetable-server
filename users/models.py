from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from common.pusher import Pusher
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
    last_activity = models.DateTimeField(blank=True, null=True)

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

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def set_device(self, params):
        token = params.get('token')
        platform = params.get('platform')
        if token and platform:
            device, created = self.device_set.get_or_create(token=token, defaults={'platform': platform,
                                                                                   'last_update': timezone.now()})

            if not created:
                device.token = token
                device.platform = platform
                device.last_update = timezone.now()
                device.save()

            return device


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
    version = models.CharField(max_length=8, null=True, blank=True, help_text='Version of API.')
    last_update = models.DateTimeField()

    def __str__(self):
        return f'{self.user} | {self.platform}'

    @classmethod
    def remove_invalid_tokens(cls):
        pusher = Pusher()
        registration_ids = cls.objects.values_list('token', flat=True)
        valid_registration_ids = pusher.fcm.clean_registration_ids(registration_ids)
        return cls.objects.exclude(token__in=valid_registration_ids).delete()
