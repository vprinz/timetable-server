from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from users.models import User


class LoginRequiredMiddleware(MiddlewareMixin):
    admin_path = '/admin/'

    def process_view(self, request, callback, callback_args, callback_kwargs):
        login_required = not (
                getattr(callback, 'login_not_required', False) or request.path.startswith(self.admin_path),
        )

        if not (request.user.is_authenticated or getattr(request, '_force_auth_user', False)) and login_required:
            return HttpResponse(status=401, content='The user must be authorized.')


class HeaderSessionMiddleware(SessionMiddleware):
    cookie_name = 'HTTP_' + settings.SESSION_COOKIE_NAME.upper()

    def process_request(self, request):
        session_key = request.META.get(self.cookie_name, None)
        if session_key:
            request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        try:
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            pass
        else:
            # First check if we need to delete this cookie.
            # The session should be deleted only if the session is entirely empty.
            if self.cookie_name in request.META and empty:
                pass
            else:
                if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                    if response.status_code != 500:
                        request.session.save()
                        response[settings.SESSION_COOKIE_NAME] = request.session.session_key
        return response


class UpdateLastActivityMiddleware(MiddlewareMixin):

    def process_request(self, request):
        assert hasattr(request, 'user'), ('The UpdateLastActivityMiddleware requires '
                                          'authentication middleware to be installed.')

        if request.user.is_authenticated:
            User.objects.filter(id=request.user.id).update(last_activity=timezone.now())
