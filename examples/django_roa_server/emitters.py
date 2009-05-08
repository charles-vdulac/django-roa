import logging

from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson

from piston.emitters import Emitter, XMLEmitter
from piston.utils import Mimer

logger = logging.getLogger("django_roa_server log")

def render_serialized_data(data, format):
    if isinstance(data, HttpResponse):
        return data
    elif isinstance(data, (int, str)):
        response = data
    else:
        response = serializers.serialize(format, data, **{'indent': True})
    logger.debug(u"Response:\n%s" % response)
    return response

class DjangoEmitter(XMLEmitter):
    """
    Django XML emitter.
    """
    def render(self, request):
        return render_serialized_data(self.data, 'xml')
    
Emitter.register('django', DjangoEmitter, 'application/xml; charset=utf-8')

class CustomDjangoEmitter(XMLEmitter):
    """
    Custom Django XML emitter.
    """
    def render(self, request):
        return render_serialized_data(self.data, 'custom')
    
Emitter.register('custom', CustomDjangoEmitter, 'application/xml; charset=utf-8')

