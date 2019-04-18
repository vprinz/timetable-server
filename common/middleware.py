from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class LoginRequiredMiddleware(MiddlewareMixin):
    admin_path = '/admin/'

    def process_view(self, request, callback, callback_args, callback_kwargs):
        login_required = not (
                getattr(callback, 'login_not_required', False) or request.path.startswith(self.admin_path)
        )

        if not (request.user.is_authenticated or getattr(request, '_force_auth_user', False)) and login_required:
            return HttpResponse(status=401, content='The user must be registered.')
