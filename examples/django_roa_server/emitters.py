import logging

from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson

from piston.emitters import Emitter, DjangoEmitter

logger = logging.getLogger("django_roa_server log")


class ROADjangoEmitter(DjangoEmitter):
    """
    ROA Django XML emitter.
    
    Just log the response with logging module.
    """
    def render(self, request):
        response = super(ROADjangoEmitter, self).render(request, 'xml')
        logger.debug(u"Response:\n%s" % response)
        return response
    
Emitter.register('django', ROADjangoEmitter, 'application/xml; charset=utf-8')

class CustomDjangoEmitter(DjangoEmitter):
    """
    Custom Django XML emitter.
    
    Use a custom serializer.
    """
    def render(self, request):
        response = super(CustomDjangoEmitter, self).render(request, 'custom')
        logger.debug(u"Response:\n%s" % response)
        return response
    
Emitter.register('custom', CustomDjangoEmitter, 'application/xml; charset=utf-8')

