from django.db import models
from django.template.defaultfilters import slugify

from django_roa import Model, Manager

class RemotePage(Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    published = models.BooleanField()
    publication_date = models.DateTimeField(blank=True, null=True)
    
    objects = Manager()
    
    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.id)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepage/'


class RemotePageWithCustomSlug(Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    
    objects = Manager()
    
    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.id)

    def save(self, force_insert=False, force_update=False):
        if not self.slug:
            self.slug = slugify(self.title)
        super(RemotePageWithCustomSlug, self).save(force_insert, force_update)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithcustomslug/'

    def get_resource_url_detail(self):
        return u"%s%s-%s/" % (self.get_resource_url_list(), self.id, self.slug)


class RemotePageWithOverriddenUrls(Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    objects = Manager()
    
    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.id)

    def save(self, force_insert=False, force_update=False):
        if not self.slug:
            self.slug = slugify(self.title)
        super(RemotePageWithOverriddenUrls, self).save(force_insert, force_update)

    @staticmethod
    def get_resource_url_list():
        return u'' # overridden by settings


