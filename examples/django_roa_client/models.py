# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify

from django_roa import Model

class RemotePage(Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepage/'


class RemotePageWithManyFields(Model):
    #auto_field = models.AutoField(primary_key=True)
    char_field = models.CharField(max_length=50, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)
    datetime_field = models.DateTimeField(blank=True, null=True)
    decimal_field = models.DecimalField(decimal_places=3, max_digits=5, blank=True, null=True)
    email_field = models.EmailField(blank=True, null=True)
    filepath_field = models.FilePathField(blank=True, null=True)
    float_field = models.FloatField(blank=True, null=True)
    integer_field = models.IntegerField(blank=True, null=True)
    ipaddress_field = models.IPAddressField(blank=True, null=True)
    positiveinteger_field = models.PositiveIntegerField(blank=True, null=True)
    positivesmallinteger_field = models.PositiveSmallIntegerField(blank=True, null=True)
    slug_field = models.SlugField(blank=True, null=True)
    smallinteger_field = models.SmallIntegerField(blank=True, null=True)
    text_field = models.TextField(blank=True, null=True)
    time_field = models.TimeField(blank=True, null=True)
    url_field = models.URLField(blank=True, null=True)
    xml_field = models.XMLField(blank=True, null=True)

    file_field = models.FileField(upload_to="files", blank=True, null=True)
    image_field = models.ImageField(upload_to="images", blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.__class__.__name__, self.pk)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithmanyfields/'


class RemotePageWithBooleanFields(Model):
    boolean_field = models.BooleanField()
    null_boolean_field = models.NullBooleanField()

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithbooleanfields/'


class RemotePageWithCustomSlug(Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.slug:
            self.slug = slugify(self.title)
        super(RemotePageWithCustomSlug, self).save(force_insert, force_update)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithcustomslug/'

    def get_resource_url_detail(self):
        return u"%s%s-%s/" % (self.get_resource_url_list(), self.pk, self.slug)


class RemotePageWithOverriddenUrls(Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.slug:
            self.slug = slugify(self.title)
        super(RemotePageWithOverriddenUrls, self).save(force_insert, force_update)

    @staticmethod
    def get_resource_url_list():
        return u'' # overridden by settings


class RemotePageWithRelationsThrough(Model):
    title = models.CharField(max_length=50)
    remote_page_with_relations = models.ForeignKey("RemotePageWithRelations", blank=True, null=True)
    remote_page_with_many_fields = models.ForeignKey("RemotePageWithManyFields", blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithrelationsthrough/'


class RemotePageWithRelations(Model):
    title = models.CharField(max_length=50)
    remote_page = models.ForeignKey(RemotePage, blank=True, null=True)
    remote_page_fields = models.ManyToManyField(RemotePageWithManyFields, through=RemotePageWithRelationsThrough, blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithrelations/'


class RemotePageWithNamedRelations(Model):
    title = models.CharField(max_length=50)
    first_page = models.ForeignKey(RemotePage, blank=True, null=True, related_name="from_first")
    last_page = models.ForeignKey(RemotePage, blank=True, null=True, related_name="from_last")

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithnamedrelations/'


class RemotePageWithProxy(RemotePage):

    class Meta:
        proxy = True

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithproxy/'

class RemotePageWithCustomPrimaryKey(Model):
    auto_field = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithcustomprimarykey/'

class RemotePageWithCustomPrimaryKeyCountOverridden(RemotePageWithCustomPrimaryKey):

    class Meta:
        proxy = True

    def get_resource_url_count(self):
        return u'http://127.0.0.1:8081/django_roa_server/remotepagewithcustomprimarykey/count2/'
