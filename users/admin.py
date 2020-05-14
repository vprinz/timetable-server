from django.contrib.admin import TabularInline, register
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from university.models import Subscription
from users.models import Device, User


class SubscriptionInline(TabularInline):
    model = Subscription
    extra = 0
    fields = ('id', 'title', 'subgroup', 'is_main', 'state', 'created', 'modified')
    readonly_fields = ('id', 'created', 'modified')


class DeviceInline(TabularInline):
    model = Device
    extra = 0
    fields = ('id', 'token', 'platform', 'version', 'last_update')


@register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('id', 'email')
    ordering = ('-id',)
    inlines = (SubscriptionInline, DeviceInline)
    readonly_fields = ('id',)

    fieldsets = (
        (None, {'fields': (
            'id',
            ('first_name', 'last_name'),
            ('email', 'password'),
            ('last_login', 'date_joined', 'last_activity')
        )}),
    )

    superuser_extra_fieldsets = (
        (_('Permissions'),
         {'fields': (
             ('is_active', 'is_staff', 'is_superuser'),
             'groups', 'user_permissions'
         )}),
    )

    def get_actions(self, request):
        result = super(UserAdmin, self).get_actions(request)
        result.pop('delete_selected', None)
        return result

    def get_fieldsets(self, request, obj=None):
        result = super(UserAdmin, self).get_fieldsets(request, obj)
        if request.user.is_superuser:
            result += self.superuser_extra_fieldsets
        return result
