import logging
from sets import Set

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.db import models
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, _get_queryset

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
            response = serializers.serialize(format, result)
            response = response.replace('_server', '_client')
            response = HttpResponse(response, mimetype=mimetype)
            return response
        return HttpResponse('OK', mimetype=mimetype)
    return wrapped


class MethodDispatcher(object):
    
    def __call__(self, request, app_label, model_name, object_id):
        """
        Dispatch the request given the method and object_id argument.
        """
        model = models.get_model(app_label, model_name)
        method = request.method
        logger.debug(u"Request: %s %s %s" % (method, model.__name__, object_id))
        if object_id is None:
            if method == 'GET':
                return self.index(request, model)
            elif method == 'POST':
                return self.add(request, model)
        else:
            object = get_object_or_404(model, id=object_id)
            if method == 'GET':
                return self.retrieve(request, model, object)
            elif method == 'PUT':
                return self.modify(request, model, object)
            elif method == 'DELETE':
                return self.delete(request, model, object)
    
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
        for field in model._meta.fields:
            field_data = data.get(field.name, None)
            if field_data not in ('', 'None'):
                if isinstance(field, models.fields.BooleanField):
                    if field_data is not None:
                        if field_data == u'True':
                            field_data = True
                        elif field_data == u'False':
                            field_data = False
                        else:
                            field_data = None
                values[field.name] = field_data
        
        for key in keys:
            if key.endswith('_id') and key not in values:
                values[str(key)] = int(data[key])
                del values[key[:-3]]
        
        object = model.objects.create(**values)
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
        keys = []
        for dict_ in data.dicts:
            keys += dict_.keys()
        keys = Set(keys).intersection(Set([f.name for f in model._meta.fields]))
        for k in keys:
            field_data = data[k]
            if field_data not in ('', 'None'):
                field = getattr(object, k)
                if isinstance(field, bool):
                    if field_data == u'True':
                        field_data = True
                    elif field_data == u'False':
                        field_data = False
                    else:
                        field_data = None
                setattr(object, k, field_data)
        object.save()
        response = [model.objects.get(id=object.id)]
        #response = [object]
        logger.debug(u'Object "%s" modified with %s' % (object, data.items()))
        return response


class MethodDispatcherWithCustomSlug(MethodDispatcher):
    
    def __call__(self, request, app_label, model_name, object_slug):
        """
        Dispatch the request given the method and object_slug argument.
        """
        model = models.get_model(app_label, model_name)
        method = request.method
        logger.debug(u"Request: %s %s %s" % (method, model.__name__, object_slug))
        if object_slug is None:
            if method == 'GET':
                return self.index(request, model)
            elif method == 'POST':
                return self.add(request, model)
        else:
            object = self.get_object_from_slug(model, object_slug)
            if method == 'GET':
                return self.retrieve(request, model, object)
            elif method == 'PUT':
                return self.modify(request, model, object)
            elif method == 'DELETE':
                return self.delete(request, model, object)

    def get_object_from_slug(self, model, object_slug):
        """Returns an object from a slug.
        
        Useful when the slug is a combination of many fields.
        """
        id, slug = object_slug.split('-', 1)
        object = get_object_or_404(model, id=id, slug=slug)
        return object
    