from django_roa.db import set_roa_headers


class ROAMiddleware(object):
    def process_request(self, request):
        # Set headers:
        set_roa_headers(request)
