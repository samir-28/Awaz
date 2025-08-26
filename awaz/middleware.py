from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware

class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        # Switch session cookie name before session loads
        if request.path.startswith('/djangoadmin/'):
            settings.SESSION_COOKIE_NAME = 'admin_sessionid'
        else:
            settings.SESSION_COOKIE_NAME = 'frontend_sessionid'
        
        super().process_request(request)

    def process_response(self, request, response):
        # Make sure to reset it here too, before saving the session cookie
        if request.path.startswith('/djangoadmin/'):
            settings.SESSION_COOKIE_NAME = 'admin_sessionid'
        else:
            settings.SESSION_COOKIE_NAME = 'frontend_sessionid'
        
        return super().process_response(request, response)