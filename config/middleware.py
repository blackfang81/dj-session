from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from session.session import SessionStore


def get_user(request):
    if not hasattr(request, "_cached_user"):
        request._cached_user = auth.get_user(request)
    return request._cached_user


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))


class YourSessionMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        session_key = request.COOKIES.get("sessionid")
        request.session = SessionStore(session_key=session_key)

    def process_response(self, request, response):
        if hasattr(request, "session"):
            if request.session.modified:
                request.session.save()
            if request.session.session_key:
                response.set_cookie(
                    "sessionid",
                    request.session.session_key,
                    max_age=60 * 60 * 24 * 14,
                    httponly=True,
                    samesite="Lax",
                )
        return response
