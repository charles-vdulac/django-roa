from django.conf import settings
from django.db.models import query
from django.core import serializers

from restclient.rest import Resource, ResourceNotFound


class Query(object):
    def __init__(self):
        self.count = False
        self.order_by = []
        self.filters = {}
        self.excludes = {}
        self.filterable = True
        self.limit_start = None
        self.limit_stop = None
        self.where = False
    
    def can_filter(self):
        return self.filterable
    
    def clone(self):
        return self
    
    def get_count(self):
        self.count = True
    
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
    
    @property
    def parameters(self):
        parameters = {}
        # Counting
        if self.count:
            parameters['count'] = True
        
        # Filtering
        for k, v in self.filters.iteritems():
            parameters['filter_%s' % k] = v
        for k, v in self.excludes.iteritems():
            parameters['exclude_%s' % k] = v
        
        # Ordering
        if self.order_by:
            order_by = ','.join(self.order_by)
            if 'remotemodel_ptr' in order_by:
                order_by = order_by.replace('remotemodel_ptr', 'id')
            parameters['order_by'] = order_by
        
        # Slicing
        if self.limit_start:
            parameters['limit_start'] = self.limit_start
        if self.limit_stop:
            parameters['limit_stop'] = self.limit_stop
        
        # Format
        parameters['format'] = getattr(settings, "ROA_FORMAT", 'json')
        
        #print parameters
        return parameters


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
        try:
            resource = Resource(self.model._meta.resource_url_list)
        except AttributeError:
            raise Exception, self.model._meta.__repr__()

        try:
            response = resource.get(**self.query.parameters)
        except ResourceNotFound:
            return

        # TODO: find a better way to do this
        response = response.replace('auth.user', 'remoteauth.remoteuser')
        response = response.replace('auth.message', 'remoteauth.remotemessage')

        for res in serializers.deserialize(getattr(settings, "ROA_FORMAT", 'json'), response):
            obj = res.object
            obj.id = obj.remotemodel_ptr_id
            yield obj
        
    def count(self):
        """
        Returns the number of records as an integer.
        
        The result is not cached nor comes from cache, cache must be handled
        by the server.
        """
        clone = self._clone()
        clone.query.get_count()
        
        resource = Resource(clone.model._meta.resource_url_list)
        
        try:
            response = resource.get(**clone.query.parameters)
        except ResourceNotFound:
            response = 0
        
        return int(response)

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
