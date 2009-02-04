import logging
from sets import Set

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.db import models
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, _get_queryset
from django.utils.encoding import smart_unicode

_MIMETYPE = {
    'json': 'application/json',
    'xml': 'application/xml'
}

# create logger
logger = logging.getLogger("django_roa_server log")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("%(name)s - %(message)s"))
# add ch to logger
logger.addHandler(ch)


def serialize(f):
    """
    Decorator to serialize responses.
    """
    def wrapped(self, request, *args, **kwargs):
        format = request.GET.get('format', 'json')
        mimetype = _MIMETYPE.get(format, 'text/plain')
        try:
            result = f(self, request, *args, **kwargs)
        except ObjectDoesNotExist:
            response = HttpResponse('ERROR', mimetype=mimetype)
            response.status_code = 404
            return response
        
        # count
        try:
            response = HttpResponse(int(result), mimetype=mimetype)
            return response
        except TypeError:
            pass
        
        if result:
            # serialization
            response = serializers.serialize(format, result, **{'indent': True})
            response = response.replace('_server', '_client')
            logger.debug(u"Response:\n%s" % response)
            response = HttpResponse(response, mimetype=mimetype)
            return response
        return HttpResponse('OK', mimetype=mimetype)
    return wrapped


class MethodDispatcher(object):
    
    def __call__(self, request, app_label, model_name, **args):
        """
        Dispatch the request given the method and object_id argument.
        """
        model = models.get_model(app_label, model_name)
        if model is None:
            logger.debug(u'Model not found with: "%s" app label and "%s" model name' % (app_label, model_name))
            raise Http404()
        method = request.method
        logger.debug(u"Request: %s %s %s" % (method, model.__name__, args))
        if len([value for value in args.values() if value is not None]):
            object = self._get_object(model, **args)
            if method == 'GET':
                return self.retrieve(request, model, object)
            elif method == 'PUT':
                return self.modify(request, model, object)
            elif method == 'DELETE':
                return self.delete(request, model, object)
        else:
            if method == 'GET':
                return self.index(request, model)
            elif method == 'POST':
                return self.add(request, model)
    
    @staticmethod
    def _get_object(model, **args):
        """
        Return an object from an object_id in args, ease subclassing.
        """
        return get_object_or_404(model, id=args['object_id'])
    
    ######################
    ## Resource methods ##
    ######################    
    @serialize
    def index(self, request, model):
        """
        Returns a list of objects given request args.
        """
        # Initialization
        queryset = _get_queryset(model)
        
        # Filtering
        filters, excludes = {}, {}
        for k, v in request.GET.iteritems():
            if k.startswith('filter_'):
                filters[k[7:]] = v
            if k.startswith('exclude_'):
                excludes[k[8:]] = v
        queryset = queryset.filter(*filters.items()).exclude(*excludes.items())
        
        # Ordering
        if 'order_by' in request.GET:
            order_bys = request.GET['order_by'].split(',')
            queryset = queryset.order_by(*order_bys)
        
        # Counting
        if 'count' in request.GET:
            counter = queryset.count()
            logger.debug(u'Count: %s objects' % counter)
            return counter
        
        # Slicing
        limit_start = int(request.GET.get('limit_start', 0))
        limit_stop = request.GET.get('limit_stop', False) and int(request.GET['limit_stop']) or None
        queryset = queryset[limit_start:limit_stop]
        
        obj_list = list(queryset)
        if not obj_list:
            raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
        logger.debug(u'Objects: %s retrieved' % obj_list)
        return obj_list

    @serialize
    def add(self, request, model):
        """
        Creates a new object given request args, returned as a list.
        """
        data = request.REQUEST.copy()
        keys = []
        for dict_ in data.dicts:
            keys += dict_.keys()
        
        values = {}
        m2m_data = {}
        for field in model._meta.local_fields:
            field_value = data.get(field.name, None)
            if field_value not in ('', 'None'):
                
                # Handle M2M relations
                if field.rel and isinstance(field.rel, models.ManyToManyRel):
                    m2m_convert = field.rel.to._meta.pk.to_python
                    m2m_data[field.name] = [m2m_convert(smart_unicode(pk)) for pk in field_value]
                
                # Handle FK fields
                elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                    field_value = data.get(field.attname, None)
                    if field_value is not None:
                        values[field.attname] = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                    else:
                        values[field.attname] = None
                
                # Handle all other fields
                else:
                    if isinstance(field, models.fields.BooleanField):
                        field_value = field.to_python(field_value)
                    elif isinstance(field, models.fields.FloatField):
                        if field_value is not None:
                            field_value = float(field_value)
                    values[field.name] = field_value
        
        object = model.objects.create(**values)
        if m2m_data:
            for accessor_name, object_list in m2m_data.items():
                setattr(object, accessor_name, object_list)
        
        response = [model.objects.get(id=object.id)]
        #response = [object]
        logger.debug(u'Object "%s" created' % object)
        return response

    ####################
    ## Object methods ##
    ####################
    @serialize
    def retrieve(self, request, model, object):
        """
        Returns an object as a list.
        """
        response = [object]
        logger.debug(u'Object "%s" retrieved' % object)
        return response
    
    @serialize
    def delete(self, request, model, object):
        """
        Deletes an object.
        """
        object.delete()
        logger.debug(u'Object "%s" deleted, remains %s' % (object, model.objects.all()))
    
    @serialize
    def modify(self, request, model, object):
        """
        Modifies an object given request args, returned as a list.
        """
        data = request.REQUEST.copy()
        
        # Add M2M relations
        if 'm2m_add' in data:
            obj_ids_str = data['m2m_ids']
            obj_ids = [int(obj_id) for obj_id in data['m2m_ids']]
            m2m_field = getattr(object, data['m2m_field_name'])
            m2m_field.add(*obj_ids)
            
            response = [model.objects.get(id=object.id)]
            #response = [object]
            logger.debug(u'Object "%s" added M2M relations with ids %s' % (object, obj_ids_str))
            return response
        
        # Remove M2M relations
        if 'm2m_remove' in data:
            obj_ids_str = data['m2m_ids']
            obj_ids = [int(obj_id) for obj_id in data['m2m_ids']]
            m2m_field = getattr(object, data['m2m_field_name'])
            m2m_field.remove(*obj_ids)
            
            response = [model.objects.get(id=object.id)]
            #response = [object]
            logger.debug(u'Object "%s" removed M2M relations with ids %s' % (object, obj_ids_str))
            return response
        
        # Remove M2M relations
        if 'm2m_clear' in data:
            m2m_field = getattr(object, data['m2m_field_name'])
            m2m_field.clear()
            
            response = [model.objects.get(id=object.id)]
            #response = [object]
            logger.debug(u'Object "%s" cleared M2M relations' % (object, ))
            return response
        
        m2m_data = {}
        for field in model._meta.local_fields:
            field_name = field.name
                
            # Handle M2M relations
            if field.rel and isinstance(field.rel, models.ManyToManyRel):
                if field_name in data:
                    field_value = data[field_name]
                    m2m_convert = field.rel.to._meta.pk.to_python
                    m2m_data[field.name] = [m2m_convert(smart_unicode(pk)) for pk in field_value]
            
            # Handle FK fields
            elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                field_value = data.get(field.attname, None)
                if field_value is not None:
                    field_value = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                setattr(object, field.attname, field_value)
            
            # Handle all other fields
            elif field_name in data:
                field_value = data[field_name]
                if field_value in ('', 'None'):
                    field_value = None
                if isinstance(field, models.fields.BooleanField):
                    if field_value is None:
                        field_value = False
                    field_value = field.to_python(field_value)
                elif isinstance(field, models.fields.IntegerField):
                    field_value = field.to_python(field_value)
                elif isinstance(field, models.fields.FloatField):
                    if field_value is not None:
                        field_value = float(field_value)
                elif isinstance(field, models.fields.CharField):
                    if field_value is None:
                        field_value = u""
                setattr(object, field_name, field_value)
        
        object.save()
        if m2m_data:
            for accessor_name, object_list in m2m_data.items():
                setattr(object, accessor_name, object_list)
        
        response = [model.objects.get(id=object.id)]
        #response = [object]
        logger.debug(u'Object "%s" modified with %s' % (object, data.items()))
        return response


class MethodDispatcherWithCustomSlug(MethodDispatcher):

    @staticmethod
    def _get_object(model, **args):
        """Returns an object from a slug.
        
        Useful when the slug is a combination of many fields.
        """
        id, slug = args['object_slug'].split('-', 1)
        object = get_object_or_404(model, id=id, slug=slug)
        return object
    