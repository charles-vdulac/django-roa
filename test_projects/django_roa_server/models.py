from django.db import models
from django.utils.translation import gettext_lazy as _

class RemotePage(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    published = models.BooleanField()
    publication_date = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.id)

