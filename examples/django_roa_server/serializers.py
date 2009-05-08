import logging

from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson

from piston.emitters import Emitter, JSONEmitter, XMLEmitter
from piston.utils import Mimer

logger = logging.getLogger("django_roa_server log")

def render_serialized_data(data, format):
    if isinstance(data, HttpResponse):
        return data
    elif isinstance(data, (int, str)):
        response = data
    else:
        response = serializers.serialize(format, data, **{'indent': True})
        response = response.replace('_server', '_client')
    logger.debug(u"Response:\n%s" % response)
    return response

class CustomJSONEmitter(JSONEmitter):
    """
    JSON emitter, understands timestamps.
    """
    def render(self, request):
        return render_serialized_data(self.data, 'json')
    
Emitter.register('json', CustomJSONEmitter, 'application/json; charset=utf-8')
Mimer.register(simplejson.loads, ('application/json',))

class CustomXMLEmitter(XMLEmitter):
    """
    Custom XML emitter.
    """
    def render(self, request):
        return render_serialized_data(self.data, 'custom')
    
Emitter.register('custom', CustomXMLEmitter, 'application/xml; charset=utf-8')
Mimer.register(lambda *a: None, ('text/xml',))
