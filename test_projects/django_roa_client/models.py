from django.db import models
from django.template.defaultfilters import slugify

from django_roa import Model, Manager

class RemotePage(Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    published = models.BooleanField()
    publication_date = models.DateTimeField(blank=True, null=True)
    
    objects = Manager()
    
    class Meta:
        resource_url_list = u'http://127.0.0.1:8081/django_roa_server/remotepage/'
    
    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.id)


class RemotePageWithCustomSlug(Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    
    objects = Manager()
    
    class Meta:
        resource_url_list = u'http://127.0.0.1:8081/django_roa_server/remotepagewithcustomslug/'
    
    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.id)

    def save(self, force_insert=False, force_update=False):
        if not self.slug:
            self.slug = slugify(self.title)
        super(RemotePageWithCustomSlug, self).save(force_insert, force_update)

    @property
    def resource_url_detail(self):
        return u"%s%s-%s/" % (self._meta.resource_url_list, self.id, self.slug)
