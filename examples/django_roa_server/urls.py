from django.conf import settings
from django.conf.urls.defaults import *

from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from django_roa_server.handlers import RemotePageHandler, \
    RemotePageWithManyFieldsHandler, RemotePageWithBooleanFieldsHandler, \
    RemotePageWithCustomSlugHandler, RemotePageWithOverriddenUrlsHandler, \
    RemotePageWithRelationsHandler, UserHandler, MessageHandler, \
    PermissionHandler, GroupHandler

remote_pages = Resource(handler=RemotePageHandler)
remote_pages_with_many_fields = Resource(handler=RemotePageWithManyFieldsHandler)
remote_pages_with_boolean_fields = Resource(handler=RemotePageWithBooleanFieldsHandler)
remote_pages_with_custom_slug = Resource(handler=RemotePageWithCustomSlugHandler)
remote_pages_with_overridden_urls = Resource(handler=RemotePageWithOverriddenUrlsHandler)
remote_pages_with_relations = Resource(handler=RemotePageWithRelationsHandler)
users = Resource(handler=UserHandler)
messages = Resource(handler=MessageHandler)
permissions = Resource(handler=PermissionHandler)
groups = Resource(handler=GroupHandler)

urlpatterns = patterns('',
    # Remote pages
    url(r'^django_roa_server/remotepage/?(?P<id>\d+)?/?$', remote_pages),
    url(r'^django_roa_server/remotepagewithmanyfields/?(?P<id>\d+)?/?$', remote_pages_with_many_fields),
    url(r'^django_roa_server/remotepagewithbooleanfields/?(?P<id>\d+)?/?$', remote_pages_with_boolean_fields),
    url(r'^django_roa_server/remotepagewithcustomslug/?(?P<object_slug>[-\w]+)?/?$', remote_pages_with_custom_slug),
    url(r'^django_roa_server/remotepagewithoverriddenurls/?(?P<object_slug>[-\w]+)?/?$', remote_pages_with_overridden_urls),
    url(r'^django_roa_server/remotepagewithrelations/?(?P<id>\d+)?/?$', remote_pages_with_relations),
    
    # Auth application
    url(r'^auth/user/?(?P<id>\d+)?/?$', users),
    url(r'^auth/message/?(?P<id>\d+)?/?$', messages),
    url(r'^auth/permission/?(?P<id>\d+)?/?$', permissions),
    url(r'^auth/group/?(?P<id>\d+)?/?$', groups),
)
