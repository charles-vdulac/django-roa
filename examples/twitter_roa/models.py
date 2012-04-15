from django.db import models

from django_roa import Model, Manager
from django_roa.db.query import RemoteQuerySet

class User(Model):
    name = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255)
    description = models.TextField()

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.screen_name)

    @staticmethod
    def get_resource_url_list():
        return u'http://api.twitter.com/1/users/lookup.json?screen_name=twitterapi,twitter,twittersearch,twittermedia,twittermobile'

    def get_resource_url_count(self):
        return User.get_resource_url_list()


class FakeCountRemoteQuerySet(RemoteQuerySet):
    def count(self):
        """
        Because trying to count the whole number of tweets is stupid.
        """
        return 20


class TweetManager(Manager):
    def get_query_set(self):
        return FakeCountRemoteQuerySet(self.model)


class Tweet(Model):
    text = models.TextField()
    source = models.CharField(max_length=50)
    user = models.ForeignKey(User)

    objects = TweetManager()

    def __unicode__(self):
        return u'%s (%s)' % (self.text, self.id)

    @staticmethod
    def get_resource_url_list():
        return u'http://api.twitter.com/1/statuses/public_timeline.json'
