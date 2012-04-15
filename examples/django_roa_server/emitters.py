import logging

from django.conf import settings

from piston.emitters import Emitter, DjangoEmitter

logger = logging.getLogger("django_roa_server")

DEFAULT_CHARSET = getattr(settings, 'DEFAULT_CHARSET', 'utf-8')

class ROADjangoEmitter(DjangoEmitter):
    """
    ROA Django XML emitter.

    Just log the response with logging module.
    """
    def render(self, request):
        response = super(ROADjangoEmitter, self).render(request, 'xml')
        logger.debug(u"Response:\n%s" % str(response).decode(DEFAULT_CHARSET))
        return response

Emitter.register('django', ROADjangoEmitter, 'application/xml; charset=utf-8')

class CustomDjangoEmitter(DjangoEmitter):
    """
    Custom Django XML emitter.

    Use a custom serializer.
    """
    def render(self, request):
        response = super(CustomDjangoEmitter, self).render(request, 'custom')
        logger.debug(u"Response:\n%s" % response.decode(DEFAULT_CHARSET))
        return response

Emitter.register('custom', CustomDjangoEmitter, 'application/xml; charset=utf-8')
