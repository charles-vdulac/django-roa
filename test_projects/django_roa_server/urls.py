from django.conf import settings
from django.conf.urls.defaults import *

from django_roa_server.views import MethodDispatcher


urlpatterns = patterns('',
    (r'^(?P<app_label>[_\w]+)/(?P<model_name>[_\w]+)/?(?P<object_id>\d+)?/?$', MethodDispatcher()),
)

#urlpatterns = patterns('django_roa_server.views',
#    (r'^([^/]+)/([^/]+)/?$', 'resource'),
#    (r'^([^/]+)/([^/]+)/(.+)/?$', 'resource_id'),
#)
