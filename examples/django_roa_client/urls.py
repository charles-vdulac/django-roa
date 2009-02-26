from django.conf.urls.defaults import *
from django.contrib import admin

from django_roa_client.views import home

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/(.*)', admin.site.root),
    url(r'^$', home),
)
