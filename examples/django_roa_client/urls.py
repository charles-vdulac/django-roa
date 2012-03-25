from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

from django_roa_client.views import home

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home),
)
