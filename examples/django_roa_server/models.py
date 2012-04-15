from django.db import models

class RemotePage(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)


class RemotePageWithManyFields(models.Model):
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


class RemotePageWithBooleanFields(models.Model):
    boolean_field = models.BooleanField()
    null_boolean_field = models.NullBooleanField()


class RemotePageWithCustomSlug(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)


class RemotePageWithOverriddenUrls(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)


class RemotePageWithRelationsThrough(models.Model):
    title = models.CharField(max_length=50)
    remote_page_with_relations = models.ForeignKey("RemotePageWithRelations", blank=True, null=True)
    remote_page_with_many_fields = models.ForeignKey("RemotePageWithManyFields", blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)


class RemotePageWithRelations(models.Model):
    title = models.CharField(max_length=50)
    remote_page = models.ForeignKey(RemotePage, blank=True, null=True)
    remote_page_fields = models.ManyToManyField(RemotePageWithManyFields, through=RemotePageWithRelationsThrough, blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)


class RemotePageWithNamedRelations(models.Model):
    title = models.CharField(max_length=50)
    first_page = models.ForeignKey(RemotePage, blank=True, null=True, related_name="from_first")
    last_page = models.ForeignKey(RemotePage, blank=True, null=True, related_name="from_last")

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)


class RemotePageWithCustomPrimaryKey(models.Model):
    auto_field = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.pk)
