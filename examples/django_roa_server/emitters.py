import logging

from django.core import serializers
from django.http import HttpResponse
from django.utils import simplejson

from piston.emitters import Emitter, XMLEmitter
from piston.utils import Mimer

logger = logging.getLogger("django_roa_server log")

class DjangoEmitter(Emitter):
    """
    Emitter for the Django serialized format.
    """
    def serialize(self, format):
        if isinstance(self.data, HttpResponse):
            return self.data
        elif isinstance(self.data, (int, str)):
            response = self.data
        else:
            response = serializers.serialize(format, self.data, indent=True)

        return response
        
    def render(self, request):
        return self.serialize(format='xml')
        
Emitter.register('django', DjangoEmitter, 'application/xml; charset=utf-8')

class CustomDjangoEmitter(DjangoEmitter):
    """
    Custom Django XML emitter.
    """
    def render(self, request):
        return self.serialize(format='custom')
    
Emitter.register('custom', CustomDjangoEmitter, 'application/xml; charset=utf-8')

