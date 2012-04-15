from django.conf import settings
from django.utils.xmlutils import SimplerXMLGenerator

from django.core.serializers.xml_serializer import Serializer as XMLSerializer, \
                                                   Deserializer as XMLDeserializer

DEFAULT_CHARSET = getattr(settings, 'DEFAULT_CHARSET', 'utf-8')

class Serializer(XMLSerializer):
    """
    A test serializer which removes ``django-objects`` xml tag from default
    Django's xml serializer, adapt it to your own usage.
    """

    def start_serialization(self):
        """
        Start serialization -- open the XML document and the root element.
        """
        self.xml = SimplerXMLGenerator(self.stream, self.options.get("encoding", DEFAULT_CHARSET))
        self.xml.startDocument()
        self.xml.startElement("django-test", {"version" : "1.0"})

    def end_serialization(self):
        """
        End serialization -- end the document.
        """
        self.indent(0)
        self.xml.endElement("django-test")
        self.xml.endDocument()


class Deserializer(XMLDeserializer):
    pass
