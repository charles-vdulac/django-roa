from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

def fake_home(request):
    from django.http import HttpResponse
    return HttpResponse('Home' * 50)

urlpatterns = patterns('',
    url(r'^admin/(.*)', admin.site.root),
    url(r'^$', fake_home),
)
