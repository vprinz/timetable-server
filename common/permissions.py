from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Disable CSRF Token for Rest API until iOS app will be able to handle it."""

    def enforce_csrf(self, request):
        return
