===========================================
Django-ROA (Resource Oriented Architecture)
===========================================

**Use Django's ORM to model remote API resources.**

Fork of original `David Larlet Django ROA lib <http://code.larlet.fr/django-roa/src>`_.
Now ROA works directly with an API like `Django Rest Framework <http://www.django-rest-framework.org/>`_

**How does it works:**
Each time a request is passed to the database, the request is intercepted and transformed to an HTTP request to the remote server with the right
method (GET, POST, PUT or DELETE) given the get_resource_url_* methods specified in the model's definition.


Documentation
=============

Initial documentation:

- `Wiki home <http://code.larlet.fr/django-roa/wiki/Home>`_
- `Getting started with Django-ROA <http://code.larlet.fr/django-roa/wiki/GettingStarted#!getting-started-with-django-roa>`_
- `Developing with Django-ROA <http://code.larlet.fr/django-roa/wiki/Development#!developing-with-django-roa>`_


Installation
============

.. code:: bash

    $ pip install -e git+https://github.com/charles-vdulac/django-roa.git@master#egg=django_roa


Fork getting started
====================

If you have an API output like this (typical DRF output):

.. code:: python

    # GET http://api.example.com/articles/
    # HTTP 200 OK
    # Content-Type: application/json
    # Vary: Accept
    # Allow: GET, POST, HEAD, OPTIONS

    {
        "count": 3,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "headline": "John's first story",
                "pub_date": "2013-01-04",
                "reporter": {
                    "id": 1,
                    "account": {
                        "id": 1,
                        "email": "john@example.com"
                    },
                    "first_name": "John",
                    "last_name": "Smith"
                }
            },
            ...
        ]
    }

Your code will look like this:

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

- Initial tests: read `documentation <http://code.larlet.fr/django-roa/wiki/GettingStarted#!running-tests>`_
- Fork tests: read `README <examples/django_rest_framework/README.md>`_


Caveats
=======

For the moment, the library doesn't work in this case:

One to one (reversed)
---------------------

.. code:: python

  class Reporter(CommonROAModel):
      account = models.OneToOneField(Account)
      ...

with fixtures:

.. code:: json

    {
        "model": "api.reporter",
        "pk": 1,
        "fields": {
            "first_name": "John",
            "last_name": "Smith",
            "account": 1
        }
    },
    {
        "model": "api.account",
        "pk": 1,
        "fields": {
            "email": "john@example.com"
        }
    },

This works:

.. code:: python

    reporter = Reporter.objects.get(id=1)
    assertEqual(reporter.account.id, 1)
    assertEqual(reporter.account.email, 'john@example.com')

But not this way:

.. code:: python

    account = Account.objects.get(id=1)
    assertEqual(account.reporter.id, 1)
    assertEqual(account.reporter.first_name, "John")


HTTPS certificate pinning
=========================

You can pass ssl args (see `ssl.wrap_socket()`) via the `ROA_SSL_ARGS` of your
``settings.py``.


To pin the server certificate, save the public certificate(s) you want to
pin in *pinned-ca.pem* and add the following to your *settings.py* :

.. code:: python

    from os.path import dirname, join
    ROA_SSL_ARGS = {
        'ca_certs': join(dirname(dirname(__file__)), 'pinned-ca.pem'),
        'cert_reqs': True
    }
