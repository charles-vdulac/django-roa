import logging

from django.conf import settings
from django.db.models import query
from django.core import serializers
from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models.query_utils import Q
from django.utils.encoding import force_unicode

from restclient import Resource, ResourceNotFound, RequestFailed
from django_roa.db.exceptions import ROAException

logger = logging.getLogger("django_roa")

ROA_MODEL_NAME_MAPPING = getattr(settings, 'ROA_MODEL_NAME_MAPPING', [])
ROA_ARGS_NAMES_MAPPING = getattr(settings, 'ROA_ARGS_NAMES_MAPPING', {})


class Query(object):
    def __init__(self):
        self.order_by = []
        self.filters = {}
        self.excludes = {}
        self.filterable = True
        self.limit_start = None
        self.limit_stop = None
        self.where = False
        self.select_related = False
        self.max_depth = None
        self.extra_select = {}
    
    def can_filter(self):
        return self.filterable
    
    def clone(self):
        return self
    
    def clear_ordering(self):
        self.order_by = []
    
    def filter(self, *args, **kwargs):
        self.filters.update(kwargs)

    def exclude(self, *args, **kwargs):
        self.excludes.update(kwargs)
    
    def set_limits(self, start=None, stop=None):
        self.limit_start = start
        self.limit_stop = stop
        self.filterable = False
    
    def add_select_related(self, fields):
        """
        Sets up the select_related data structure so that we only select
        certain related models (as opposed to all models, when
        self.select_related=True).
        """
        field_dict = {}
        for field in fields:
            d = field_dict
            for part in field.split(LOOKUP_SEP):
                d = d.setdefault(part, {})
        self.select_related = field_dict
        self.related_select_cols = []
        self.related_select_fields = []
    
    @property
    def parameters(self):
        """
        Returns useful parameters as a dictionary.
        """
        parameters = {}
        
        # Filtering
        for k, v in self.filters.iteritems():
            parameters['%s%s' % (ROA_ARGS_NAMES_MAPPING.get('FILTER_', 'filter_'), k)] = v
        for k, v in self.excludes.iteritems():
            parameters['%s%s' % (ROA_ARGS_NAMES_MAPPING.get('EXCLUDE_', 'exclude_'), k)] = v
        
        # Ordering
        if self.order_by:
            order_by = ','.join(self.order_by)
            parameters[ROA_ARGS_NAMES_MAPPING.get('ORDER_BY', 'order_by')] = order_by
        
        # Slicing
        if self.limit_start:
            parameters[ROA_ARGS_NAMES_MAPPING.get('LIMIT_START', 'limit_start')] = self.limit_start
        if self.limit_stop:
            parameters[ROA_ARGS_NAMES_MAPPING.get('LIMIT_STOP', 'limit_stop')] = self.limit_stop
        
        # Format
        ROA_FORMAT = getattr(settings, "ROA_FORMAT", 'json')
        parameters[ROA_ARGS_NAMES_MAPPING.get('FORMAT', 'format')] = ROA_FORMAT
        
        parameters.update(getattr(settings, 'ROA_CUSTOM_ARGS', {}))
        return parameters
    
    ##########################################
    # Fake methods required by admin options #
    ##########################################
    
    def add_fields(self, field_names, allow_m2m=True):
        """ Fake method. """
        pass
    
    def trim_extra_select(self, names):
        """ Fake method. """
        pass
    
    def results_iter(self):
        """ Fake method. """
        return []

    def combine(self, rhs, connector):
        """ Fake method. """
        pass


class RemoteQuerySet(query.QuerySet):
    """
    QuerySet which access remote resources.
    """
    def __init__(self, model=None, query=None):
        self.model = model
        self.query = query or Query()
        self._result_cache = None
        self._iter = None
        self._sticky_filter = False
        
        self.params = {}
    
    ########################
    # PYTHON MAGIC METHODS #
    ########################

    def __repr__(self):
        if not self.query.limit_start and not self.query.limit_stop:
            data = list(self[:query.REPR_OUTPUT_SIZE + 1])
            if len(data) > query.REPR_OUTPUT_SIZE:
                data[-1] = "...(remaining elements truncated)..."
        else:
            data = list(self)
        return repr(data)

    ####################################
    # METHODS THAT DO RESOURCE QUERIES #
    ####################################

    def iterator(self):
        """
        An iterator over the results from applying this QuerySet to the
        remote web service.
        """
        resource = Resource(self.model.get_resource_url_list())

        try:
            parameters = self.query.parameters
            logger.debug(u"""Requesting: "%s" through %s
                          with parameters "%s" """ % (
                          self.model.__name__, 
                          resource.uri, 
                          force_unicode(parameters)))
            response = resource.get(**parameters)
        except ResourceNotFound:
            return
        except Exception, e:
            raise ROAException(e)

        response = force_unicode(response).encode(settings.DEFAULT_CHARSET)
        for local_name, remote_name in ROA_MODEL_NAME_MAPPING:
            response = response.replace(remote_name, local_name)
        
        ROA_FORMAT = getattr(settings, "ROA_FORMAT", 'json')
        for res in serializers.deserialize(ROA_FORMAT, response):
            obj = res.object
            yield obj
        
    def count(self):
        """
        Returns the number of records as an integer.
        
        The result is not cached nor comes from cache, cache must be handled
        by the server.
        """
        clone = self._clone()
        
        # Instantiation of clone.model is necessary because we can't set
        # a staticmethod for get_resource_url_count and avoid to set it
        # for all model without relying on get_resource_url_list
        instance = clone.model()
        resource = Resource(instance.get_resource_url_count())
        
        try:
            parameters = clone.query.parameters
            logger.debug(u"""Counting  : "%s" through %s
                          with parameters "%s" """ % (
                clone.model.__name__, 
                resource.uri, 
                force_unicode(parameters)))
            response = resource.get(**parameters)
        except Exception, e:
            raise ROAException(e)
        
        return int(response)

    def _get_from_id(self, id):
        """
        Returns an object given an id, request directly with the
        get_resource_url_detail method without filtering on ids
        (as Django's ORM do).
        """
        clone = self._clone()
        
        # Instantiation of clone.model is necessary because we can't set
        # a staticmethod for get_resource_url_detail and avoid to set it
        # for all model without relying on get_resource_url_list
        instance = clone.model()
        instance.id = id
        resource = Resource(instance.get_resource_url_detail())
        
        try:
            parameters = clone.query.parameters
            logger.debug(u"""Retrieving : "%s" through %s
                          with parameters "%s" """ % (
                clone.model.__name__, 
                resource.uri, 
                force_unicode(parameters)))
            response = resource.get(**parameters)
        except Exception, e:
            raise ROAException(e)
        
        response = force_unicode(response).encode(settings.DEFAULT_CHARSET)
        for local_name, remote_name in ROA_MODEL_NAME_MAPPING:
            response = response.replace(remote_name, local_name)
        
        ROA_FORMAT = getattr(settings, "ROA_FORMAT", 'json')
        deserializer = serializers.get_deserializer(ROA_FORMAT)
        if hasattr(deserializer, 'deserialize_object'):
            result = deserializer(response).deserialize_object(response)
        else:
            result = deserializer(response).next()
        
        return result.object
        
    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        # special case, get(id=X) directly request the resource URL and do not
        # filter on ids like Django's ORM do.
        if kwargs.keys() == ['id']:
            return self._get_from_id(kwargs['id'])
        else:
            return super(RemoteQuerySet, self).get(*args, **kwargs)

    def latest(self, field_name=None):
        """
        Returns the latest object, according to the model's 'get_latest_by'
        option or optional given field_name.
        """
        latest_by = field_name or self.model._meta.get_latest_by
        assert bool(latest_by), "latest() requires either a field_name parameter or 'get_latest_by' in the model"
        
        self.query.order_by.append('-%s' % latest_by)
        return self.iterator().next()

    def delete(self):
        """
        Deletes the records in the current QuerySet.
        """
        assert self.query.can_filter(), \
                "Cannot use 'limit' or 'offset' with delete."

        del_query = self._clone()

        # Disable non-supported fields.
        del_query.query.select_related = False
        del_query.query.clear_ordering()

        for obj in del_query:
            obj.delete()

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
    delete.alters_data = True

    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################

    def filter(self, *args, **kwargs):
        """
        Returns a filtered QuerySet instance.
        """
        if args or kwargs:
            assert self.query.can_filter(), \
                    "Cannot filter a query once a slice has been taken."

        clone = self._clone()
        clone.query.filter(*args, **kwargs)
        return clone

    def exclude(self, *args, **kwargs):
        """
        Returns a filtered QuerySet instance.
        """
        if args or kwargs:
            assert self.query.can_filter(), \
                    "Cannot filter a query once a slice has been taken."

        clone = self._clone()
        clone.query.exclude(*args, **kwargs)
        return clone

    def complex_filter(self, filter_obj):
        """
        Returns a new QuerySet instance with filter_obj added to the filters.

        filter_obj can be a Q object (or anything with an add_to_query()
        method) or a dictionary of keyword lookup arguments.

        This exists to support framework features such as 'limit_choices_to',
        and usually it will be more natural to use other methods.
        """
        if isinstance(filter_obj, Q) or hasattr(filter_obj, 'add_to_query'):
            raise ROAException('Not implemented yet')
        return self.filter(**filter_obj)

    def select_related(self, *fields, **kwargs):
        """
        Returns a new QuerySet instance that will select related objects.

        If fields are specified, they must be ForeignKey fields and only those
        related objects are included in the selection.
        """
        depth = kwargs.pop('depth', 0)
        if kwargs:
            raise TypeError('Unexpected keyword arguments to select_related: %s'
                    % (kwargs.keys(),))
        obj = self._clone()
        if fields:
            if depth:
                raise TypeError('Cannot pass both "depth" and fields to select_related()')
            obj.query.add_select_related(fields)
        else:
            obj.query.select_related = True
        if depth:
            obj.query.max_depth = depth
        return obj

    def order_by(self, *field_names):
        """
        Returns a QuerySet instance with the ordering changed.
        """
        assert self.query.can_filter(), \
                "Cannot reorder a query once a slice has been taken."
        
        clone = self._clone()
        for field_name in field_names:
            clone.query.order_by.append(field_name)
        return clone

    #################################
    # METHODS THAT DO M2M RELATIONS #
    #################################

    def _add_items(self, source_col_name=None, target_col_name=None, 
                   join_table=None, pk_val=None, instance=None, field=None, 
                   *objs):
        """
        Adds m2m relations between ``instance`` object and ``objs``.
        """
        if objs:
            from django.db.models.base import Model
            # Check that all the objects are of the right type
            existing_ids = set(obj.id for obj in field.value_from_object(instance))
            for obj in objs:
                if isinstance(obj, self.model):
                    existing_ids.add(obj._get_pk_val())
                elif isinstance(obj, Model):
                    raise TypeError, "'%s' instance expected" % self.model._meta.object_name
                else:
                    existing_ids.add(obj)
            # FIXME: ugly but we set manually updated_ids to the instance
            # before saving it, get back in save_model to send appropriated
            # ids to the server
            setattr(instance, '%s_updated_ids' % field.attname, existing_ids)
            instance.save()

    def _remove_items(self, source_col_name=None, target_col_name=None, 
                      join_table=None, pk_val=None, instance=None, field=None, 
                      *objs):
        """
        Removes m2m relations between ``instance`` object and ``objs``.
        """
        if objs:
            from django.db.models.base import Model
            # Check that all the objects are of the right type
            existing_ids = set(obj.id for obj in field.value_from_object(instance))
            for obj in objs:
                if isinstance(obj, self.model):
                    existing_ids.remove(obj._get_pk_val())
                elif isinstance(obj, Model):
                    raise TypeError, "'%s' instance expected" % self.model._meta.object_name
                else:
                    existing_ids.remove(obj)
            setattr(instance, '%s_updated_ids' % field.attname, existing_ids)
            instance.save()

    def _clear_items(self, source_col_name=None, join_table=None, pk_val=None, 
                     instance=None, field=None):
        """
        Clears m2m relations related to ``instance`` object.
        """
        setattr(instance, '%s_updated_ids' % field.attname, [])
        instance.save()


    ###################
    # PRIVATE METHODS #
    ###################

    def _as_url(self):
        """
        Returns the internal query's URL and parameters 
        
        as (u'url', {'arg_key': 'arg_value'}).
        """
        return self.model.get_resource_url_list(), self.query.parameters
