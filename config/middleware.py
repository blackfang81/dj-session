from urllib.parse import urlsplit
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from session.models import Session


def get_user(request):
    if not hasattr(request, "_cached_user"):
        request._cached_user = auth.get_user(request)
    return request._cached_user


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))

class YourSessionMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        request.user = AnonymousUser()

        session_key = request.COOKIES.get("sessionid")

        if not session_key:
            return

        try:
            session = Session.objects.get(session_key=session_key)

            if session.expires_at > timezone.now():
                request.user = session.user

        except Session.DoesNotExist:
            pass
