from threading import local
from django.conf import settings


ROA_SESSION_HEADERS_KEY = 'roa_session_headers_key'


# Current thread access token:
_roa_headers = local()


def set_roa_headers(request, headers=None):

    if headers:
        request.session[ROA_SESSION_HEADERS_KEY] = headers
    elif ROA_SESSION_HEADERS_KEY in request.session:
        headers = request.session[ROA_SESSION_HEADERS_KEY]
    else:
        headers = {}

    # Save it into current thread
    _roa_headers.value = headers


def get_roa_headers():
    headers = getattr(settings, 'ROA_HEADERS', {}).copy()
    thread_headers = getattr(_roa_headers, 'value', {})
    headers.update(thread_headers)
    return headers


def reset_roa_headers():
    if hasattr(_roa_headers, 'value'):
        del _roa_headers.value
