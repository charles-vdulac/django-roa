import logging

from django.conf import settings
from django.contrib.auth.models import User, Message, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.db import models
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, _get_queryset
from django.utils.encoding import smart_unicode

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

from django_roa_server.models import RemotePage, RemotePageWithManyFields, \
    RemotePageWithBooleanFields, RemotePageWithCustomSlug, \
    RemotePageWithOverriddenUrls, RemotePageWithRelations, \
    RemotePageWithNamedRelations, RemotePageWithRelationsThrough

logger = logging.getLogger("django_roa_server")


class ROAHandler(BaseHandler):

    def flatten_dict(self, dct):
        return dict([ (str(k), dct.get(k)) for k in dct.keys() \
            if (k, dct.get(k)) != (u'id', u'None')])

    @staticmethod
    def _get_object(model, *args, **kwargs):
        return get_object_or_404(model, id=kwargs['id'])
        
    def read(self, request, *args, **kwargs):
        """
        Retrieves an object or a list of objects.
        """
        if not self.has_model():
            return rc.NOT_IMPLEMENTED
        
        if kwargs.values() != [None]:
            # Returns a single object
            return [self._get_object(self.model, *args, **kwargs)]
        
        # Initialization
        queryset = _get_queryset(self.model)
        
        # Filtering
        filters, excludes = {}, {}
        for k, v in request.GET.iteritems():
            if k.startswith('filter_'):
                filters[k[7:]] = v
            if k.startswith('exclude_'):
                excludes[k[8:]] = v
        queryset = queryset.filter(*filters.items()).exclude(*excludes.items())
        
        # Ordering (test custom parameters' name)
        if 'order' in request.GET:
            order_bys = request.GET['order'].split(',')
            queryset = queryset.order_by(*order_bys)
        
        # Slicing
        limit_start = int(request.GET.get('limit_start', 0))
        limit_stop = request.GET.get('limit_stop', False) and int(request.GET['limit_stop']) or None
        queryset = queryset[limit_start:limit_stop]
        
        obj_list = list(queryset)
        if not obj_list:
            raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
        logger.debug('Objects: %s retrieved' % [unicode(obj).encode(settings.DEFAULT_CHARSET) for obj in obj_list])
        return queryset
        
    def create(self, request, *args, **kwargs):
        """
        Creates an object given request args, returned as a list.
        """
        if not self.has_model():
            return rc.NOT_IMPLEMENTED
        
        data = request.POST.copy()
        keys = data.keys()
        
        values = {}
        for field in self.model._meta.local_fields:
            field_value = data.get(field.name, None)
            
            if field_value not in (u'', u'None'):
                
                # Handle FK fields
                if field.rel and isinstance(field.rel, models.ManyToOneRel):
                    field_value = data.get(field.attname, None)
                    if field_value not in (u'', u'None'):
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

        object = self.model.objects.create(**values)
        
        response = [self.model.objects.get(id=object.id)]
        #response = [object]
        logger.debug('Object "%s" created' % unicode(object).encode(settings.DEFAULT_CHARSET))
        return response

    def update(self, request, *args, **kwargs):
        """
        Modifies an object given request args, returned as a list.
        """
        if not self.has_model():
            return rc.NOT_IMPLEMENTED
        
        data = request.PUT.copy()
        logger.debug('Received: %s as PUT data' % data)
        object = self._get_object(self.model, *args, **kwargs)
        
        for field in self.model._meta.local_fields:
            field_name = field.name
            
            # Handle FK fields
            if field.rel and isinstance(field.rel, models.ManyToOneRel):
                field_value = data.get(field.attname, None)
                if field_value not in (u'', u'None', None):
                    field_value = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                else:
                    field_value = None
                setattr(object, field.attname, field_value)
            
            # Handle all other fields
            elif field_name in data:
                field_value = data[field_name]
                if field_value in (u'', u'None'):
                    field_value = None
                if isinstance(field, models.fields.BooleanField) \
                or isinstance(field, models.fields.NullBooleanField) \
                or isinstance(field, models.fields.IntegerField):
                    field_value = field.to_python(field_value)
                elif isinstance(field, models.fields.FloatField):
                    if field_value is not None:
                        field_value = float(field_value)
                elif isinstance(field, models.fields.CharField):
                    if field_value is None:
                        field_value = u''
                setattr(object, field_name, field_value)
        
        object.save()
        
        response = [self.model.objects.get(id=object.id)]
        #response = [object]
        logger.debug('Object "%s" modified with %s' % (
            unicode(object).encode(settings.DEFAULT_CHARSET), 
            unicode(data.items()).encode(settings.DEFAULT_CHARSET)))
        return response

    def delete(self, request, *args, **kwargs):
        """
        Deletes an object.
        """
        if not self.has_model():
            raise NotImplementedError
        
        try:
            object = self._get_object(self.model, *args, **kwargs)
            object.delete()
            logger.debug('Object "%s" deleted, remains %s' % (
                unicode(object).encode(settings.DEFAULT_CHARSET), 
                [unicode(object).encode(settings.DEFAULT_CHARSET) for object in self.model.objects.all()]))

            return rc.DELETED
        except self.model.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY
        except self.model.DoesNotExist:
            return rc.NOT_HERE


class ROACountHandler(BaseHandler):
    allowed_methods = ('GET', )

    def read(self, request, *args, **kwargs):
        """
        Retrieves the number of objects.
        """
        if not self.has_model():
            return rc.NOT_IMPLEMENTED
        
        # Initialization
        queryset = _get_queryset(self.model)
        
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
        counter = queryset.count()
        logger.debug('Count: %s objects' % counter)
        return counter


class ROAWithSlugHandler(ROAHandler):
    
    @staticmethod
    def _get_object(model, *args, **kwargs):
        """Returns an object from a slug.
        
        Useful when the slug is a combination of many fields.
        """
        id, slug = kwargs['object_slug'].split('-', 1)
        object = get_object_or_404(model, id=id, slug=slug)
        return object
    

class RemotePageHandler(ROAHandler):
    model = RemotePage

class RemotePageCountHandler(ROACountHandler):
    model = RemotePage


class RemotePageWithManyFieldsHandler(ROAHandler):
    model = RemotePageWithManyFields

class RemotePageWithManyFieldsCountHandler(ROACountHandler):
    model = RemotePageWithManyFields


class RemotePageWithBooleanFieldsHandler(ROAHandler):
    model = RemotePageWithBooleanFields

class RemotePageWithBooleanFieldsCountHandler(ROACountHandler):
    model = RemotePageWithBooleanFields


class RemotePageWithCustomSlugHandler(ROAWithSlugHandler):
    model = RemotePageWithCustomSlug

class RemotePageWithCustomSlugCountHandler(ROACountHandler):
    model = RemotePageWithCustomSlug

    
class RemotePageWithOverriddenUrlsHandler(ROAWithSlugHandler):
    model = RemotePageWithOverriddenUrls

class RemotePageWithOverriddenUrlsCountHandler(ROACountHandler):
    model = RemotePageWithOverriddenUrls


class RemotePageWithRelationsHandler(ROAHandler):
    model = RemotePageWithRelations

class RemotePageWithRelationsCountHandler(ROACountHandler):
    model = RemotePageWithRelations

    
class RemotePageWithRelationsThroughHandler(ROAHandler):
    model = RemotePageWithRelationsThrough

class RemotePageWithRelationsThroughCountHandler(ROACountHandler):
    model = RemotePageWithRelationsThrough

    
class RemotePageWithNamedRelationsHandler(ROAHandler):
    model = RemotePageWithNamedRelations

class RemotePageWithNamedRelationsCountHandler(ROACountHandler):
    model = RemotePageWithNamedRelations

    
class UserHandler(ROAHandler):
    model = User

class MessageHandler(ROAHandler):
    model = Message

class PermissionHandler(ROAHandler):
    model = Permission
    
class GroupHandler(ROAHandler):
    model = Group
