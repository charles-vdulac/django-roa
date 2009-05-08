import logging

from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson

from piston.emitters import Emitter, JSONEmitter as PistonJSONEmitter, \
                            XMLEmitter as PistonXMLEmitter
from piston.utils import Mimer

logger = logging.getLogger("django_roa_server log")

class JSONEmitter(PistonJSONEmitter):
    """
    JSON emitter, understands timestamps.
    """
    def render(self, request):
        if isinstance(self.data, HttpResponse):
            return self.data
        elif isinstance(self.data, (int, str)):
            response = self.data
        else:
            response = serializers.serialize('json', self.data, **{'indent': True})
            response = response.replace('_server', '_client')
        logger.debug(u"Response:\n%s" % response)
        return response
    
Emitter.register('json', JSONEmitter, 'application/json; charset=utf-8')
Mimer.register(simplejson.loads, ('application/json',))

class CustomXMLEmitter(PistonXMLEmitter):
    """
    Custom XML emitter.
    """
    def render(self, request):
        if isinstance(self.data, HttpResponse):
            return self.data
        elif isinstance(self.data, (int, str)):
            response = self.data
        else:
            response = serializers.serialize('custom', self.data, **{'indent': True})
            response = response.replace('_server', '_client')
        logger.debug(u"Response:\n%s" % response)
        return response
    
Emitter.register('custom', CustomXMLEmitter, 'application/xml; charset=utf-8')
Mimer.register(lambda *a: None, ('text/xml',))


