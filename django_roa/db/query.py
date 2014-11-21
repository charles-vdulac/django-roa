import logging
from StringIO import StringIO

from django.conf import settings
from django.db.models import query
from django.core import serializers
# Django >= 1.5
from django_roa.db import get_roa_headers

try:
    from django.db.models.constants import LOOKUP_SEP
#Django < 1.4
except:
    from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models.query_utils import Q
from django.utils.encoding import force_unicode

from restkit import Resource, ResourceNotFound
from django_roa.db.exceptions import ROAException, ROANotImplementedYetException

logger = logging.getLogger("django_roa")

ROA_MODEL_NAME_MAPPING = getattr(settings, 'ROA_MODEL_NAME_MAPPING', [])
ROA_ARGS_NAMES_MAPPING = getattr(settings, 'ROA_ARGS_NAMES_MAPPING', {})
ROA_FORMAT = getattr(settings, 'ROA_FORMAT', 'json')
ROA_FILTERS = getattr(settings, 'ROA_FILTERS', {})
ROA_SSL_ARGS = getattr(settings, 'ROA_SSL_ARGS', {})

DEFAULT_CHARSET = getattr(settings, 'DEFAULT_CHARSET', 'utf-8')


class Query(object):
    def __init__(self):
        self.order_by = []
        self.extra_order_by = []
        self.default_ordering = []
        self.filters = {}
        self.excludes = {}
        self.search_term = None
        self.filterable = True
        self.limit_start = None
        self.limit_stop = None
        self.where = False
        self.select_related = False
        self.max_depth = None
        self.extra_select = {}
        self.select_for_update = False

    def can_filter(self):
        return self.filterable

    def clone(self):
        return self

    def clear_ordering(self):
        self.order_by = []

    def filter(self, *args, **kwargs):
        self.filters.update(kwargs)

    def search(self, search_term, limit_start=None, limit_stop=None):
        self.search_term = search_term
        self.limit_start = limit_start
        self.limit_stop = limit_stop

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
            key = '%s%s' % (ROA_ARGS_NAMES_MAPPING.get('FILTER_', 'filter_'), k)
            # v could be an object
            try:
                v = v.id
            except:
                pass

            if key in ROA_ARGS_NAMES_MAPPING:
                parameters[ROA_ARGS_NAMES_MAPPING[key]] = v
            else:
                parameters[key] = v
        for k, v in self.excludes.iteritems():
            key = '%s%s' % (ROA_ARGS_NAMES_MAPPING.get('EXCLUDE_', 'exclude_'), k)
            if key in ROA_ARGS_NAMES_MAPPING:
                parameters[ROA_ARGS_NAMES_MAPPING[key]] = v
            else:
                parameters[key] = v
        if self.search_term:
            parameters[ROA_ARGS_NAMES_MAPPING.get('SEARCH_', 'search')] = self.search_term

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

    def has_results(self, *args, **kwargs):
        """ Fake method. """
        return True


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
        self._db = False
        self._for_write = False
        self._hints = {}

        self.params = {}

        self._prefetch_related_lookups = False

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
        resource = Resource(self.model.get_resource_url_list(),
                            filters=ROA_FILTERS, **ROA_SSL_ARGS)
        try:
            parameters = self.query.parameters
            logger.debug(u"""Requesting: "%s" through %s with parameters "%s" """ % (
                          self.model.__name__,
                          resource.uri,
                          force_unicode(parameters)))
            response = resource.get(headers=self._get_http_headers(), **parameters)
        except ResourceNotFound:
            return
        except Exception as e:
            raise ROAException(e)

        response = force_unicode(response.body_string()).encode(DEFAULT_CHARSET)

        # Deserializing objects:
        data = self.model.get_parser().parse(StringIO(response))

        # Check limit_start and limit_stop arguments for pagination and only
        # slice data if they are both numeric and there are results left to go.
        # We only perform this check on lists.
        limit_start = getattr(self.query, 'limit_start', None)
        limit_stop = getattr(self.query, 'limit_stop', None)
        if (isinstance(limit_start, int) and isinstance(limit_stop, int) and
           limit_stop - limit_start < len(data) and limit_stop <= len(data) and
           isinstance(data, list)):
                data = data[limit_start:limit_stop]

        # [] is the case of empty no-paginated result
        if data != []:
            serializer = self.model.get_serializer(data=data)
            if not serializer.is_valid():
                raise ROAException(u'Invalid deserialization for %s model: %s' % (self.model, serializer.errors))

            for obj in serializer.object:
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
        resource = Resource(instance.get_resource_url_count(),
                            filters=ROA_FILTERS, **ROA_SSL_ARGS)
        try:
            parameters = clone.query.parameters
            logger.debug(u"""Counting  : "%s" through %s with parameters "%s" """ % (
                clone.model.__name__,
                resource.uri,
                force_unicode(parameters)))
            response = resource.get(headers=self._get_http_headers(), **parameters)
        except Exception as e:
            raise ROAException(e)

        response = force_unicode(response.body_string()).encode(DEFAULT_CHARSET)
        data = self.model.get_parser().parse(StringIO(response))
        return self.model.count_response(data)

    def _get_from_id_or_pk(self, id=None, pk=None, **kwargs):
        """
        Returns an object given an id or pk, request directly with the
        get_resource_url_detail method without filtering on ids
        (as Django's ORM do).
        """
        clone = self._clone()

        # Instantiation of clone.model is necessary because we can't set
        # a staticmethod for get_resource_url_detail and avoid to set it
        # for all model without relying on get_resource_url_list
        instance = clone.model()
        if pk is None:
            instance.id = id
        else:
            instance.pk = pk
        extra_args = {}
        extra_args.update(kwargs)
        extra_args.update(ROA_SSL_ARGS)
        resource = Resource(instance.get_resource_url_detail(),
                            filters=ROA_FILTERS,
                            **extra_args)
        try:
            parameters = clone.query.parameters
            logger.debug(u"""Retrieving : "%s" through %s with parameters "%s" """ % (
                clone.model.__name__,
                resource.uri,
                force_unicode(parameters)))
            response = resource.get(headers=self._get_http_headers(), **parameters)
        except Exception as e:
            raise ROAException(e)

        response = force_unicode(response.body_string()).encode(DEFAULT_CHARSET)

        for local_name, remote_name in ROA_MODEL_NAME_MAPPING:
            response = response.replace(remote_name, local_name)

        # Deserializing objects:
        data = self.model.get_parser().parse(StringIO(response))
        serializer = self.model.get_serializer(data=data)
        if not serializer.is_valid():
            raise ROAException(u'Invalid deserialization for %s model: %s' % (self.model, serializer.errors))

        return serializer.object

    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        # special case, get(id=X) directly request the resource URL and do not
        # filter on ids like Django's ORM do.

        # keep the custom attribute name of model for later use
        custom_pk = self.model._meta.pk.attname
        # search PK, ID or custom PK attribute name for exact match and get set
        # of unique matches
        attributes_set = set(attr for attr in ['id__exact', 'pk__exact', '%s__exact' % custom_pk] if attr in kwargs.keys())
        exact_match = list(attributes_set)
        # common way of getting particular object
        if kwargs.keys() == ['id']:
            return self._get_from_id_or_pk(id=kwargs['id'])
        # useful for admin which relies on PKs
        elif kwargs.keys() == ['pk']:
            return self._get_from_id_or_pk(pk=kwargs['pk'])
        # check the case of PK attribute with custom name
        elif kwargs.keys() == [custom_pk]:
            return self._get_from_id_or_pk(pk=kwargs[custom_pk])
        # check if there's an exact match filter
        elif len(exact_match) == 1:
            # use the value of exact match filter to retrieve object by PK
            return self._get_from_id_or_pk(pk=kwargs[exact_match[0]])
        else:
            # filter the request rather than retrieve it through get method
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

    def search(self, search_term, limit_start=None, limit_stop=None, *args, **kwargs):
        """
        Returns a filtered QuerySet instance.
        """
        assert not(args or kwargs), "Search accept only one arg (search_term) and limit_start/limit_stop kwargs"

        clone = self._clone()
        clone.query.search(search_term, limit_start=limit_start, limit_stop=limit_stop)
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

    def extra(self, select=None, where=None, params=None, tables=None,
              order_by=None, select_params=None):
        """
        Only to handle the case of the "cute trick" used in ModelForms (and
        per extension admin) for unique and date constraints.

        Example: ``.extra(select={'a': 1}).values('a').order_by()``.

        http://code.djangoproject.com/browser/django/trunk/django/forms/models.py#L322
        is an interesting documentation for details.
        """
        assert self.query.can_filter(), \
                "Cannot change a query once a slice has been taken"
        if select == {'a': 1}:
            # Totally hackish but we need a fake object to deal with
            # successive calls to values and order_by based on a count
            # which is the less expensive action for our implementation.
            class FakeInt(object):
                def __init__(self, count):
                    self.count = count

                def values(self, *fields):
                    if fields == ('a',): # double check that it's our case
                        return self

                def order_by(self):
                    return self.count

            return FakeInt(self.count())
        raise ROANotImplementedYetException('extra is not yet fully implemented.')

    ###################
    # PRIVATE METHODS #
    ###################

    def _clone(self, klass=None, setup=False, **kwargs):
        if klass is None:
            klass = self.__class__
        query = self.query.clone()
        if self._sticky_filter:
            query.filter_is_sticky = True
        c = klass(model=self.model, query=query)
        c.__dict__.update(kwargs)
        if setup and hasattr(c, '_setup_query'):
            c._setup_query()
        return c

    def _as_url(self):
        """
        Returns the internal query's URL and parameters

        as (u'url', {'arg_key': 'arg_value'}).
        """
        return self.model.get_resource_url_list(), self.query.parameters


    def _get_http_headers(self):
        return get_roa_headers()
