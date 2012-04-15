import logging

from django.contrib.auth.models import User, Message, Group, Permission
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404, _get_queryset

from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc

from django_roa_server.models import RemotePage, RemotePageWithManyFields, \
    RemotePageWithBooleanFields, RemotePageWithCustomSlug, \
    RemotePageWithOverriddenUrls, RemotePageWithRelations, \
    RemotePageWithNamedRelations, RemotePageWithRelationsThrough, \
    RemotePageWithCustomPrimaryKey

logger = logging.getLogger("django_roa_server")


class ROAHandler(BaseHandler):

    def flatten_dict(self, dct):
        return dict([ (str(k), dct.get(k)) for k in dct.keys() \
            if (k, dct.get(k)) != (u'id', u'None') and (k, dct.get(k)) != (u'pk', u'None')])

    @staticmethod
    def _get_object(model, *args, **kwargs):
        return get_object_or_404(model, pk=kwargs['pk'])

    def read(self, request, *args, **kwargs):
        """
        Retrieves an object or a list of objects.
        """
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        logger.debug('Args: %s' % str(args))
        logger.debug('Kwargs: %s' % str(kwargs))

        if kwargs.values() != [None]:
            # Returns a single object
            return [self._get_object(self.model, *args, **kwargs)]

        # Initialization
        queryset = _get_queryset(self.model)
        logger.debug('Before filters: %s' % str(queryset))

        # Filtering
        filters, excludes = {}, {}
        for k, v in request.GET.iteritems():
            if k.startswith('filter_'):
                filters[k[7:]] = v
            if k.startswith('exclude_'):
                excludes[k[8:]] = v
        queryset = queryset.filter(*filters.items()).exclude(*excludes.items())

        logger.debug('Filters: %s' % str(filters))
        logger.debug('Excludes: %s' % str(excludes))
        logger.debug('After filters: %s' % str(queryset))

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
        logger.debug(u'Objects: %s retrieved' % [unicode(obj) for obj in obj_list])
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Creates an object given request args, returned as a list.
        """
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        data = request.POST.copy()

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

        obj = self.model.objects.create(**values)

        response = [self.model.objects.get(pk=obj.pk)]
        logger.debug(u'Object "%s" created' % unicode(obj))
        return response

    def update(self, request, *args, **kwargs):
        """
        Modifies an object given request args, returned as a list.
        """
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        data = request.PUT.copy()
        logger.debug(u'Received: %s as PUT data' % data)
        obj = self._get_object(self.model, *args, **kwargs)

        for field in self.model._meta.local_fields:
            field_name = field.name

            # Handle FK fields
            if field.rel and isinstance(field.rel, models.ManyToOneRel):
                field_value = data.get(field.attname, None)
                if field_value not in (u'', u'None', None):
                    field_value = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
                else:
                    field_value = None
                setattr(obj, field.attname, field_value)

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
                setattr(obj, field_name, field_value)

        obj.save()

        response = [self.model.objects.get(pk=obj.pk)]
        logger.debug(u'Object "%s" modified with %s' % (
            unicode(obj), unicode(data.items())))
        return response

    def delete(self, request, *args, **kwargs):
        """
        Deletes an object.
        """
        if not self.has_model():
            raise NotImplementedError

        try:
            obj = self._get_object(self.model, *args, **kwargs)
            obj.delete()
            logger.debug(u'Object "%s" deleted, remains %s' % (
                unicode(obj),
                [unicode(obj) for obj in self.model.objects.all()]))

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
        logger.debug(u'Count: %s objects' % counter)
        return counter


class ROAWithSlugHandler(ROAHandler):

    @staticmethod
    def _get_object(model, *args, **kwargs):
        """Returns an object from a slug.

        Useful when the slug is a combination of many fields.
        """
        pk, slug = kwargs['object_slug'].split('-', 1)
        obj = get_object_or_404(model, pk=pk)
        return obj


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

class RemotePageWithCustomPrimaryKeyHandler(ROAHandler):
    model = RemotePageWithCustomPrimaryKey

class RemotePageWithCustomPrimaryKeyCountHandler(ROACountHandler):
    model = RemotePageWithCustomPrimaryKey

class RemotePageWithCustomPrimaryKeyCount2Handler(ROACountHandler):
    model = RemotePageWithCustomPrimaryKey

    def read(self, request, *args, **kwargs):
        return 'invalid counter'


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
