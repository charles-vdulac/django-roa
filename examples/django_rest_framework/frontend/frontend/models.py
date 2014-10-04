from django.db import models
from django_roa import Model as ROAModel


class CommonROAModel(ROAModel):

    class Meta:
        abstract = True

    @classmethod
    def get_resource_url_list(cls):
        return u'http://127.0.0.1:8000/%s/' % (cls.api_base_name)

    def get_resource_url_count(self):
        return self.get_resource_url_list()


# Declare backend models


class Account(CommonROAModel):
    id = models.IntegerField(primary_key=True)  # don't forget it !
    email = models.CharField(max_length=30)

    api_base_name = 'accounts'

    @classmethod
    def serializer(cls):
        from .serializers import AccountSerializer
        return AccountSerializer


class Reporter(CommonROAModel):
    id = models.IntegerField(primary_key=True)  # don't forget it !
    account = models.OneToOneField(Account)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    api_base_name = 'reporters'

    @classmethod
    def serializer(cls):
        from .serializers import ReporterSerializer
        return ReporterSerializer


class Article(CommonROAModel):
    id = models.IntegerField(primary_key=True)  # don't forget it !
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(Reporter, related_name='articles')

    api_base_name = 'articles'

    @classmethod
    def serializer(cls):
        from .serializers import ArticleSerializer
        return ArticleSerializer


class Tag(CommonROAModel):
    id = models.IntegerField(primary_key=True)  # don't forget it !
    label = models.CharField(max_length=30)
    articles = models.ManyToManyField(Article, related_name='tags')

    api_base_name = 'tags'

    @classmethod
    def serializer(cls):
        from .serializers import TagSerializer
        return TagSerializer
