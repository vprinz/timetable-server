from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, UserAdmin

from university.models import Subscription
from .models import User


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email')
    ordering = ('-id',)
    inlines = (SubscriptionInline,)

    fieldsets = (
        (None, {'fields': (
            ('first_name', 'last_name'),
            ('email',),
            ('password')
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
