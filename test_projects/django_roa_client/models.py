from django.db import models
from django.utils.translation import gettext_lazy as _

from django_roa import Model, Manager

class RemotePage(Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    published = models.BooleanField()
    
    objects = Manager()
    
    class Meta:
        resource_url_list = u'http://127.0.0.1:8081/django_roa_server/remotepage/'
    
    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.id)
