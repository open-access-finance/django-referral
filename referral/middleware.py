from . import settings
from .models import Referrer


class ReferrerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        if settings.GET_PARAMETER in request.GET:
            referrer = None
            referrer_name = request.GET.get(settings.GET_PARAMETER, '').strip()
            if not referrer_name:
                return
            try:
                if settings.CASE_SENSITIVE:
                    referrer = Referrer.objects.get(name=referrer_name)
                else:
                    referrer = Referrer.objects.get(name__iexact=referrer_name)
            except Referrer.DoesNotExist:
                if settings.AUTO_CREATE:
                    referrer = Referrer(name=referrer_name)
                    referrer.save()
                if referrer is not None and settings.AUTO_ASSOCIATE:
                    referrer.match_campaign()
            finally:
                if referrer is not None:
                    request.session[settings.SESSION_KEY] = referrer.pk
