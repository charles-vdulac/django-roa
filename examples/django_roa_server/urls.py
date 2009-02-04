from django.conf import settings
from django.conf.urls.defaults import *

from django_roa_server.views import MethodDispatcher, MethodDispatcherWithCustomSlug

urlpatterns = patterns('',
    (r'^(?P<app_label>[_\w]+)/(?P<model_name>[_\w]+)/?(?P<object_id>\d+)?/?$', MethodDispatcher()),
    (r'^(?P<app_label>[_\w]+)/(?P<model_name>[_\w]+)/?(?P<object_slug>[-\w]+)?/?$', MethodDispatcherWithCustomSlug()),
)
