from django.utils import timezone


class AdminTimezoneMiddleware:
    """
    If the request path starts with /control-room1/, switch to IST.
    Otherwise leave Django in UTC.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/control-room1"):
            timezone.activate("Asia/Kolkata")
        # else: it remains in settings.TIME_ZONE (UTC)

        response = self.get_response(request)

        # clean up for next request
        timezone.deactivate()
        return response
