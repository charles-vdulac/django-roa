import logging

from django.core import serializers
from django.http import HttpResponse

from piston.emitters import Emitter, JSONEmitter as PistonJSONEmitter

_MIMETYPE = {
    'json': 'application/json',
    'xml': 'application/xml'
}

logger = logging.getLogger("django_roa_server log")

class JSONEmitter(PistonJSONEmitter):
    """
    JSON emitter, understands timestamps.
    """
    def render(self, request):
        format = request.GET.get('format', 'json')
        mimetype = _MIMETYPE.get(format, 'text/plain')
        # serialization
        if isinstance(self.data, HttpResponse):
            return self.data
        elif isinstance(self.data, int) or isinstance(self.data, str):
            response = self.data
        else:
            response = serializers.serialize(format, self.data, **{'indent': True})
            response = response.replace('_server', '_client')
        logger.debug(u"Response:\n%s" % response)
        response = HttpResponse(response, mimetype=mimetype)

        return response
    
Emitter.register('json', JSONEmitter, 'application/json; charset=utf-8')

class CustomXMLEmitter(PistonJSONEmitter):
    """
    Custom XML emitter.
    """
    def render(self, request):
        format = request.GET.get('format', 'json')
        mimetype = _MIMETYPE.get(format, 'text/plain')
        # serialization
        if isinstance(self.data, HttpResponse):
            return self.data
        elif isinstance(self.data, int) or isinstance(self.data, str):
            response = self.data
        else:
            response = serializers.serialize(format, self.data, **{'indent': True})
            response = response.replace('_server', '_client')
        logger.debug(u"Response:\n%s" % response)
        response = HttpResponse(response, mimetype=mimetype)

        return response
    
Emitter.register('custom', CustomXMLEmitter, 'application/xml; charset=utf-8')


