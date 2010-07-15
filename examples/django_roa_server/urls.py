from django.conf import settings
from django.conf.urls.defaults import *

from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from django_roa_server.handlers import RemotePageHandler, \
    RemotePageWithManyFieldsHandler, RemotePageWithBooleanFieldsHandler, \
    RemotePageWithCustomSlugHandler, RemotePageWithOverriddenUrlsHandler, \
    RemotePageWithRelationsHandler, UserHandler, MessageHandler, \
    PermissionHandler, GroupHandler, RemotePageCountHandler, \
    RemotePageWithManyFieldsCountHandler, RemotePageWithBooleanFieldsCountHandler, \
    RemotePageWithCustomSlugCountHandler, RemotePageWithOverriddenUrlsCountHandler, \
    RemotePageWithRelationsHandler, RemotePageWithNamedRelationsHandler, \
    RemotePageWithNamedRelationsCountHandler, RemotePageWithRelationsThroughHandler

remote_pages = Resource(handler=RemotePageHandler)
remote_pages_count = Resource(handler=RemotePageCountHandler)

remote_pages_with_many_fields = Resource(handler=RemotePageWithManyFieldsHandler)
remote_pages_with_many_fields_count = Resource(handler=RemotePageWithManyFieldsCountHandler)

remote_pages_with_boolean_fields = Resource(handler=RemotePageWithBooleanFieldsHandler)
remote_pages_with_boolean_fields_count = Resource(handler=RemotePageWithBooleanFieldsCountHandler)

remote_pages_with_custom_slug = Resource(handler=RemotePageWithCustomSlugHandler)
remote_pages_with_custom_slug_count = Resource(handler=RemotePageWithCustomSlugCountHandler)

remote_pages_with_overridden_urls = Resource(handler=RemotePageWithOverriddenUrlsHandler)
remote_pages_with_overridden_urls_count = Resource(handler=RemotePageWithOverriddenUrlsCountHandler)

remote_pages_with_relations = Resource(handler=RemotePageWithRelationsHandler)
remote_pages_with_relations_count = Resource(handler=RemotePageWithRelationsHandler)

remote_pages_with_relations_through = Resource(handler=RemotePageWithRelationsThroughHandler)
remote_pages_with_relations_through_count = Resource(handler=RemotePageWithRelationsThroughHandler)

remote_pages_with_named_relations = Resource(handler=RemotePageWithNamedRelationsHandler)
remote_pages_with_named_relations_count = Resource(handler=RemotePageWithNamedRelationsCountHandler)

users = Resource(handler=UserHandler)
messages = Resource(handler=MessageHandler)
permissions = Resource(handler=PermissionHandler)
groups = Resource(handler=GroupHandler)

urlpatterns = patterns('',
    # Remote pages counts
    url(r'^django_roa_server/remotepage/count/$', remote_pages_count),
    url(r'^django_roa_server/remotepagewithmanyfields/count/$', remote_pages_with_many_fields_count),
    url(r'^django_roa_server/remotepagewithbooleanfields/count/$', remote_pages_with_boolean_fields_count),
    url(r'^django_roa_server/remotepagewithcustomslug/count/$', remote_pages_with_custom_slug_count),
    url(r'^django_roa_server/remotepagewithoverriddenurls/count/$', remote_pages_with_overridden_urls_count),
    url(r'^django_roa_server/remotepagewithrelations/count/$', remote_pages_with_relations_count),
    url(r'^django_roa_server/remotepagewithrelationsthrough/count/$', remote_pages_with_relations_through_count),
    url(r'^django_roa_server/remotepagewithnamedrelations/count/$', remote_pages_with_named_relations_count),
    url(r'^django_roa_server/remotepagewithproxy/count/$', remote_pages_count),
    
    # Remote pages
    url(r'^django_roa_server/remotepage/?(?P<id>\d+)?/?$', remote_pages),
    url(r'^django_roa_server/remotepagewithmanyfields/?(?P<id>\d+)?/?$', remote_pages_with_many_fields),
    url(r'^django_roa_server/remotepagewithbooleanfields/?(?P<id>\d+)?/?$', remote_pages_with_boolean_fields),
    url(r'^django_roa_server/remotepagewithcustomslug/?(?P<object_slug>[-\w]+)?/?$', remote_pages_with_custom_slug),
    url(r'^django_roa_server/remotepagewithoverriddenurls/?(?P<object_slug>[-\w]+)?/?$', remote_pages_with_overridden_urls),
    url(r'^django_roa_server/remotepagewithrelations/?(?P<id>\d+)?/?$', remote_pages_with_relations),
    url(r'^django_roa_server/remotepagewithrelationsthrough/?(?P<id>\d+)?/?$', remote_pages_with_relations_through),
    url(r'^django_roa_server/remotepagewithnamedrelations/?(?P<id>\d+)?/?$', remote_pages_with_named_relations),
    url(r'^django_roa_server/remotepagewithproxy/?(?P<id>\d+)?/?$', remote_pages),
    
    # Auth application
    url(r'^auth/user/?(?P<id>\d+)?/?$', users),
    url(r'^auth/message/?(?P<id>\d+)?/?$', messages),
    url(r'^auth/permission/?(?P<id>\d+)?/?$', permissions),
    url(r'^auth/group/?(?P<id>\d+)?/?$', groups),
)
