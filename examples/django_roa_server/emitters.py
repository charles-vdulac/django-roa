import logging

from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson

from piston.emitters import Emitter, DjangoEmitter

logger = logging.getLogger("django_roa_server")


class ROADjangoEmitter(DjangoEmitter):
    """
    ROA Django XML emitter.
    
    Just log the response with logging module.
    """
    def render(self, request):
        response = super(ROADjangoEmitter, self).render(request, 'xml')
        logger.debug("Response:\n%s" % str(response).decode(settings.DEFAULT_CHARSET))
        return response
    
Emitter.register('django', ROADjangoEmitter, 'application/xml; charset=utf-8')

class CustomDjangoEmitter(DjangoEmitter):
    """
    Custom Django XML emitter.
    
    Use a custom serializer.
    """
    def render(self, request):
        response = super(CustomDjangoEmitter, self).render(request, 'custom')
        logger.debug("Response:\n%s" % response.decode(settings.DEFAULT_CHARSET))
        return response
    
Emitter.register('custom', CustomDjangoEmitter, 'application/xml; charset=utf-8')

