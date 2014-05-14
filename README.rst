===========================================
Django-ROA (Resource Oriented Architecture)
===========================================

**Use Django's ORM to model remote API resources.**

Fork of original `David Larlet Django ROA lib <http://code.larlet.fr/django-roa/src>`_.
Now ROA works directly with an API like `Django Rest Framework <http://www.django-rest-framework.org/>`_

**How does it works :**
Each time a request is passed to the database, the request is intercepted and transformed to an HTTP request to the remote server with the right
method (GET, POST, PUT or DELETE) given the get_resource_url_* methods specified in the model's definition.


Documentation
=============

Initial documentation:

 * `Wiki home <http://code.larlet.fr/django-roa/wiki/Home>`_
 * `Getting started with Django-ROA <http://code.larlet.fr/django-roa/wiki/GettingStarted#!getting-started-with-django-roa>`_
 * `Developing with Django-ROA <http://code.larlet.fr/django-roa/wiki/Development#!developing-with-django-roa>`_


Installation
============

.. code:: bash

    $ pip install -e git+https://github.com/charles-vdulac/django-roa/.git@master#egg=django_roa


Fork getting started
====================

.. code:: python

    from django.db import models
    from django_roa import Model as ROAModel

    class Article(ROAModel):
        id = models.IntegerField(primary_key=True)  # don't forget it !
        headline = models.CharField(max_length=100)
        pub_date = models.DateField()
        reporter = models.ForeignKey(Reporter, related_name='articles')

        api_base_name = 'articles'

        @classmethod
        def serializer(cls):
            from .serializers import ArticleSerializer
            return ArticleSerializer

        @classmethod
        def get_resource_url_list(cls):
            return u'http://api.example.com/{base_name}/'.format(
                base_name=cls.api_base_name,
            )

        def get_resource_url_count(self):
            return self.get_resource_url_list()

.. code:: python

    from rest_framework import serializers
    from .models import Article

    class ArticleSerializer(serializers.ModelSerializer):
        reporter = ReporterSerializer()
        class Meta:
            model = Article
            fields = ('id', 'headline', 'pub_date', 'reporter')

Refer to `tests <examples/django_rest_framework/>`_ for full example.

Running tests
=============

 * Initial tests: read `documentation <http://code.larlet.fr/django-roa/wiki/GettingStarted#!running-tests>`_
 * Fork tests: read `README <examples/django_rest_framework/README.md>`_


