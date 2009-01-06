r"""
==========
Django ROA
==========

Tests
=====

How to run tests
----------------

First, you need to create the remote database, go to
``test_projects/django_roa_server`` and run ``syncdb`` command with 
``--noinput`` option in order to create a superuser named "david" from 
fixtures::

    $ python manage.py syncdb --noinput

Now you can launch the project's server on port 8081 in order to test this 
suite with this command::

    $ python manage.py runserver 8081

Then you can go to ``test_projects/django_roa_client`` and run this command::

    $ python manage.py test

It should return no error and you will be able to see logs from the test
server which confirm that it works as expected: remote requests are done.

Note: do not try to launch tests' projects if you put ``django_roa`` 
application into your own project, otherwise it will fail. Django do not 
handle very well projects inside projects.


Initialization
--------------

First of all, we verify that remote classes are called::

    >>> from django_roa_client.models import RemotePage
    >>> RemotePage.objects.__class__
    <class 'django_roa.db.managers.ROAManager'>
    >>> RemotePage.__class__
    <class 'django_roa.db.models.ROAModelBase'>


Base
----

Now, let's create, update, retrieve and delete a simple object::

    >>> page = RemotePage.objects.create(title=u'A first remote page')
    >>> page
    <RemotePage: A first remote page (1)>
    >>> page.title = u'Another title'
    >>> page.save()
    >>> page = RemotePage.objects.get(title=u'Another title')
    >>> page.title
    u'Another title'
    >>> pages = RemotePage.objects.all()
    >>> pages
    [<RemotePage: Another title (1)>]
    >>> page.delete()
    >>> RemotePage.objects.all()
    []
    >>> RemotePage.objects.count()
    0

A more complex example with empty values::

    >>> page = RemotePage.objects.create(title=u'')
    >>> page.title
    u''
    >>> page.title = u'A temporary title'
    >>> page.save()
    >>> page = RemotePage.objects.get(title=u'A temporary title')
    >>> page.title
    u'A temporary title'
    >>> RemotePage.objects.count()
    1
    >>> page.title = u''
    >>> page.save()
    >>> page = RemotePage.objects.all()[0]
    >>> page.title
    u''
    >>> page.delete()
    >>> RemotePage.objects.all()
    []
    >>> RemotePage.objects.count()
    0



Fields
------

First things first, we verify that default attributes are set to ``None`` or
empty values even when it comes from the server::

    >>> from django_roa_client.models import RemotePageWithManyFields
    >>> default_page = RemotePageWithManyFields.objects.create()
    >>> for field in default_page._meta.fields:
    ...     print field.name, field.value_to_string(default_page)
    id 1
    boolean_field None
    char_field None
    date_field 
    datetime_field 
    decimal_field None
    email_field None
    filepath_field None
    float_field None
    integer_field None
    ipaddress_field None
    nullboolean_field None
    positiveinteger_field None
    positivesmallinteger_field None
    slug_field None
    smallinteger_field None
    text_field None
    time_field 
    url_field None
    xml_field None
    file_field 
    image_field 
    >>> default_page = RemotePageWithManyFields.objects.get(id=default_page.id)
    >>> for field in default_page._meta.fields:
    ...     print field.name, field.value_to_string(default_page)
    id 1
    boolean_field None
    char_field None
    date_field 
    datetime_field 
    decimal_field None
    email_field None
    filepath_field None
    float_field None
    integer_field None
    ipaddress_field None
    nullboolean_field None
    positiveinteger_field None
    positivesmallinteger_field None
    slug_field None
    smallinteger_field None
    text_field None
    time_field 
    url_field None
    xml_field None
    file_field 
    image_field 

Now for each field, we will test both creation and modification of the value.

Boolean
~~~~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(boolean_field=True)
    >>> page.boolean_field
    True
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.boolean_field
    True
    >>> page.boolean_field = False
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.boolean_field
    False
    >>> page.delete()

Char
~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(char_field=u"foo")
    >>> page.char_field
    u'foo'
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.char_field
    u'foo'
    >>> page.char_field = u"bar"
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.char_field
    u'bar'
    >>> page.delete()

Date
~~~~
::

    >>> from datetime import date
    >>> page = RemotePageWithManyFields.objects.create(date_field=date(2008, 12, 24))
    >>> page.date_field
    datetime.date(2008, 12, 24)
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.date_field
    datetime.date(2008, 12, 24)
    >>> page.date_field = date(2008, 12, 25)
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.date_field
    datetime.date(2008, 12, 25)
    >>> page.delete()

DateTime
~~~~~~~~
::

    >>> from datetime import datetime
    >>> page = RemotePageWithManyFields.objects.create(datetime_field=datetime(2008, 12, 24, 11, 53, 57))
    >>> page.datetime_field
    datetime.datetime(2008, 12, 24, 11, 53, 57)
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.datetime_field
    datetime.datetime(2008, 12, 24, 11, 53, 57)
    >>> page.datetime_field = datetime(2008, 12, 25, 13, 20)
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.datetime_field
    datetime.datetime(2008, 12, 25, 13, 20)
    >>> page.delete()

Decimal
~~~~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(decimal_field=1.55)
    >>> page.decimal_field
    1.55
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.decimal_field
    Decimal("1.55")
    >>> page.decimal_field = 20.09
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.decimal_field
    Decimal("20.09")
    >>> page.delete()

Email
~~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(email_field=u"david@example.com")
    >>> page.email_field
    u'david@example.com'
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.email_field
    u'david@example.com'
    >>> page.email_field = u"david@example.org"
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.email_field
    u'david@example.org'
    >>> page.delete()

FilePath
~~~~~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(filepath_field=u"/foo/bar.zip")
    >>> page.filepath_field
    u'/foo/bar.zip'
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.filepath_field
    u'/foo/bar.zip'
    >>> page.filepath_field = u"/foo/bar/baz.tar.gz"
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.filepath_field
    u'/foo/bar/baz.tar.gz'
    >>> page.delete()

Float
~~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(float_field=1.55)
    >>> page.float_field
    1.55
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.float_field
    1.55
    >>> page.float_field = 20.09
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.float_field
    20.09
    >>> page.delete()

Integer
~~~~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(integer_field=155)
    >>> page.integer_field
    155
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.integer_field
    155
    >>> page.integer_field = 2009
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.integer_field
    2009
    >>> page.delete()

Slug
~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(slug_field=u"foo-bar")
    >>> page.slug_field
    u'foo-bar'
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.slug_field
    u'foo-bar'
    >>> page.slug_field = u"bar-baz"
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.slug_field
    u'bar-baz'
    >>> page.delete()

Text
~~~~
::

    >>> page = RemotePageWithManyFields.objects.create(text_field=u"foo bar")
    >>> page.text_field
    u'foo bar'
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.text_field
    u'foo bar'
    >>> page.text_field = u"bar baz"
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.text_field
    u'bar baz'
    >>> page.delete()

Time
~~~~
::

    >>> from datetime import time
    >>> page = RemotePageWithManyFields.objects.create(time_field=time(3, 51, 28))
    >>> page.time_field
    datetime.time(3, 51, 28)
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.time_field
    datetime.time(3, 51, 28)
    >>> page.time_field = time(11, 20, 53)
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.time_field
    datetime.time(11, 20, 53)
    >>> page.delete()

URL
~~~
::

    >>> page = RemotePageWithManyFields.objects.create(url_field=u"http://example.com")
    >>> page.url_field
    u'http://example.com'
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.url_field
    u'http://example.com'
    >>> page.url_field = u"http://example.org"
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.url_field
    u'http://example.org'
    >>> page.delete()


QuerySet API
------------

Get or create::

    >>> page2 = RemotePage.objects.create(title='A second remote page')
    >>> page3 = RemotePage.objects.create(title='A third remote page')

    >>> RemotePage.objects.get_or_create(title='A second remote page')
    (<RemotePage: A second remote page (1)>, False)
    >>> page4, created = RemotePage.objects.get_or_create(title='A fourth remote page')
    >>> created
    True

Latest::

    >>> RemotePage.objects.latest('id')
    <RemotePage: A fourth remote page (3)>
    >>> RemotePage.objects.latest('title')
    <RemotePage: A third remote page (2)>

Filtering::

    >>> RemotePage.objects.exclude(id=2)
    [<RemotePage: A second remote page (1)>, <RemotePage: A fourth remote page (3)>]

    >>> RemotePage.objects.filter(title__iexact='a FOURTH remote page')
    [<RemotePage: A fourth remote page (3)>]
    >>> RemotePage.objects.filter(title__contains='second')
    [<RemotePage: A second remote page (1)>]

Ordering::

    >>> RemotePage.objects.order_by('title')
    [<RemotePage: A fourth remote page (3)>, <RemotePage: A second remote page (1)>, <RemotePage: A third remote page (2)>]
    >>> page5 = RemotePage.objects.create(title='A fourth remote page')
    >>> RemotePage.objects.order_by('-title', '-id')
    [<RemotePage: A third remote page (2)>, <RemotePage: A second remote page (1)>, <RemotePage: A fourth remote page (4)>, <RemotePage: A fourth remote page (3)>]

Slicing::

    >>> RemotePage.objects.all()[1:3]
    [<RemotePage: A third remote page (2)>, <RemotePage: A fourth remote page (3)>]
    >>> RemotePage.objects.all()[0]
    <RemotePage: A second remote page (1)>

Combined::

    >>> page6 = RemotePage.objects.create(title='A fool remote page')
    >>> RemotePage.objects.exclude(title__contains='fool').order_by('title', '-id')[:2]
    [<RemotePage: A fourth remote page (4)>, <RemotePage: A fourth remote page (3)>]


Admin
-----

Remote users are defined in ``django_roa.remoteauth`` application::

    >>> from django_roa.remoteauth.models import RemoteUser, Message
    >>> RemoteUser.objects.all()
    [<RemoteUser: david>]
    >>> alice = RemoteUser.objects.create_user(username="alice", password="secret", email="alice@example.com")
    >>> alice.is_superuser
    False
    >>> RemoteUser.objects.all()
    [<RemoteUser: david>, <RemoteUser: alice>]
    >>> alice.id
    2
    >>> Message.objects.all()
    []
    >>> message = Message.objects.create(user=alice, message=u"Test message")
    >>> message.message
    u'Test message'
    >>> message.user
    <RemoteUser: alice>
    >>> Message.objects.all()
    [<Message: Test message>]
    >>> alice.message_set.all()
    [<Message: Test message>]

``select_related`` is not supported, we just verify that it doesn't break::

    >>> Message.objects.all().select_related()
    [<Message: Test message>]
    >>> Message.objects.all().select_related('user')
    [<Message: Test message>]

Now we can try to log in and navigate into the built-in admin::

    >>> from django.test.client import Client
    >>> c = Client()
    >>> RemoteUser.objects.create_superuser(username="bob", password="secret", email="bob@example.com")
    >>> bob = RemoteUser.objects.get(username="bob")
    >>> bob.is_superuser
    True
    >>> c.login(username="bob", password="secret")
    True
    >>> response = c.get("/admin/")
    >>> response.context[-1]["user"]
    <RemoteUser: bob>
    >>> response = c.get("/admin/django_roa_client/remotepage/")
    >>> response.status_code
    200
    >>> response.context[-1]["cl"].result_list
    [<RemotePage: A fool remote page (5)>, <RemotePage: A fourth remote page (4)>]
    >>> response.context[-1]["cl"].result_count
    5

    
Custom slug
-----------

The default URL for a resource is ``/{resource_name}/{resource_id}/`` but you 
can customize both parts, here is an example with the ``resource_id`` part 
which contains both an ``id`` and a ``slug``::

    >>> from django_roa_client.models import RemotePageWithCustomSlug
    >>> page_custom = RemotePageWithCustomSlug.objects.create(title=u"Test custom page")
    >>> page_custom.slug
    u'test-custom-page'
    >>> page_custom = RemotePageWithCustomSlug.objects.get(title=u"Test custom page")
    >>> page_custom
    <RemotePageWithCustomSlug: Test custom page (1)>
    >>> page_custom.delete()


Overriding URLs
---------------

You can override ``get_resource_url_*`` methods on a per-installation basis
with ``ROA_URL_OVERRIDES_*`` settings::
    

    >>> from django.conf import settings
    >>> settings.ROA_URL_OVERRIDES_LIST
    {'django_roa_client.remotepagewithoverriddenurls': u'http://127.0.0.1:8081/django_roa_server/remotepagewithoverriddenurls/'}
    >>> settings.ROA_URL_OVERRIDES_DETAIL
    {'django_roa_client.remotepagewithoverriddenurls': <function <lambda> at ...>}
    >>> from django_roa_client.models import RemotePageWithOverriddenUrls
    >>> page_overridden = RemotePageWithOverriddenUrls.objects.create(title=u"Test overridden urls")
    >>> page_overridden.slug
    u'test-overridden-urls'
    >>> page_overridden = RemotePageWithOverriddenUrls.objects.get(title=u"Test overridden urls")
    >>> page_overridden
    <RemotePageWithOverriddenUrls: Test overridden urls (1)>
    >>> page_overridden.delete()


Errors
------

Unicity::

    >>> RemoteUser.objects.create_user(username="alice", password="secret", email="alice@example.com")
    Traceback (most recent call last):
    ...
    ROAException: IntegrityError at /auth/user: column username is not unique
     Request Method: POST
     Request URL: http://127.0.0.1:8081/auth/user
     Exception Type: IntegrityError
     Exception Value: column username is not unique
     Exception Location: ..., line ...
     Status code: 500


Clean up
--------
::

    >>> RemotePage.objects.all().delete()
    >>> RemotePageWithManyFields.objects.all().delete()
    >>> RemotePageWithCustomSlug.objects.all().delete()
    >>> RemotePageWithOverriddenUrls.objects.all().delete()
    >>> RemoteUser.objects.exclude(username="david").delete()

"""
