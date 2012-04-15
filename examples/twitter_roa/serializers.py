import simplejson
from StringIO import StringIO

from django.conf import settings
from django.db import models
from django.utils.encoding import smart_unicode
from django.core.serializers import base
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.python import _get_model

DEFAULT_CHARSET = getattr(settings, 'DEFAULT_CHARSET', 'utf-8')

class Serializer(JSONSerializer):
    pass


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if isinstance(stream_or_string, basestring):
        stream = StringIO(stream_or_string)
    else:
        stream = stream_or_string
    models.get_apps()
    object_list = simplejson.load(stream)
    if not isinstance(object_list, list):
        object_list = [object_list]
    for obj in object_list:
        # Look up the model and starting build a dict of data for it.
        if 'screen_name' in obj:
            Model = _get_model('twitter_roa.user')
        else:
            Model = _get_model("twitter_roa.tweet")
        data = {}
        m2m_data = {}

        # Handle each field
        for (field_name, field_value) in obj.iteritems():
            if isinstance(field_value, str):
                field_value = smart_unicode(
                                field_value,
                                options.get("encoding", DEFAULT_CHARSET),
                                strings_only=True)

            try:
                field = Model._meta.get_field(field_name)
            except models.FieldDoesNotExist:
                continue

            # Handle FK fields
            if field.rel and isinstance(field.rel, models.ManyToOneRel):
                if field_value is not None:
                    data[field.attname] = field.rel.to._meta.\
                        get_field(field.rel.field_name).\
                        to_python(field_value['id'])
                else:
                    data[field.attname] = None

            # Handle all other fields
            else:
                data[field.name] = field.to_python(field_value)
        yield base.DeserializedObject(Model(**data), m2m_data)
