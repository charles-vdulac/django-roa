from rest_framework import viewsets
from django.db import models
from functools import reduce
import operator


class FilterByKeyMixin(object):
    """
    Custom viewset: add filter_key feature
    """
    search_param = 'search'
    order_param = 'order_by'
    filter_param_prefix = 'filter_'

    def construct_search(self, field_name):
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.QUERY_PARAMS.get(self.search_param, '')
        return params.replace(',', ' ').split()

    def filter_queryset(self, queryset):
        """
        Parses QUERY_PARAMS and apply them
        """

        for param in self.request.QUERY_PARAMS.keys():
            # filter ?
            if param.startswith(self.filter_param_prefix):
                key_ = param.split(self.filter_param_prefix)[1]
                value_ = self.request.QUERY_PARAMS[param]
                if value_ is not None:
                    queryset = queryset.filter(**{'%s' % (key_): value_})

            # order by ?
            elif param == self.order_param:
                value_ = self.request.QUERY_PARAMS[param]
                if value_ is not None:
                    queryset = queryset.order_by(value_)

            # search  ?
            elif param == self.search_param:
                search_fields = getattr(self, 'search_fields', None)
                if search_fields:
                    orm_lookups = [self.construct_search(str(search_field)) for search_field in search_fields]

                    for search_term in self.get_search_terms(self.request):
                        or_queries = [models.Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups]
                        queryset = queryset.filter(reduce(operator.or_, or_queries))

        limit_start = self.request.QUERY_PARAMS.get('limit_start', None)
        limit_stop = self.request.QUERY_PARAMS.get('limit_stop', None)

        if limit_stop is not None:
            limit_start = int(limit_start) if limit_start is not None else 0
            limit_stop = int(limit_stop)
            queryset = queryset[limit_start:limit_stop]

        elif limit_start is not None:
            limit_start = int(limit_start)
            queryset = queryset[limit_start:]

        return queryset


class ModelViewSet(FilterByKeyMixin, viewsets.ModelViewSet):
    pass
