# -*- coding: utf-8 -*-
r"""
==========
Django ROA
==========

Tests
=====

How to run tests
----------------

First, you need to create the remote database, go to
``examples/django_roa_server`` and run ``syncdb`` command with 
``--noinput`` option in order to create a superuser named "roa_user" from 
fixtures::

    $ python manage.py syncdb --noinput

Now you can launch the project's server on port 8081 in order to test this 
suite with this command::

    $ python manage.py runserver 8081

Then you can go to ``examples/django_roa_client`` and run this command::

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
    >>> RemotePage.objects.count() # test custom mapping too
    0


Unicode
-------
::

    >>> RemotePage.objects.all()
    []
    >>> emilie = RemotePage.objects.create(title=u"\xc9milie")
    >>> print emilie
    Émilie (1)
    >>> emilie = RemotePage.objects.get(title=u"\xc9milie")
    >>> emilie
    <RemotePage: Émilie (1)>
    >>> emilie.delete()


Fields
------

First things first, we verify that default attributes are set to ``None`` or
empty values even when it comes from the server::

    >>> from django_roa_client.models import RemotePageWithManyFields
    >>> default_page = RemotePageWithManyFields.objects.create()
    >>> for field in default_page._meta.fields:
    ...     print field.name, field.value_to_string(default_page)
    id 1
    char_field None
    date_field 
    datetime_field 
    decimal_field None
    email_field None
    filepath_field None
    float_field None
    integer_field None
    ipaddress_field None
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
    char_field None
    date_field 
    datetime_field 
    decimal_field None
    email_field None
    filepath_field None
    float_field None
    integer_field None
    ipaddress_field None
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
    >>> default_page.delete()


Same for boolean fields::

    >>> from django_roa_client.models import RemotePageWithBooleanFields
    >>> boolean_page = RemotePageWithBooleanFields.objects.create(boolean_field=True)
    >>> for field in boolean_page._meta.fields:
    ...     print field.name, field.value_to_string(boolean_page)
    id 1
    boolean_field True
    null_boolean_field None
    >>> boolean_page = RemotePageWithBooleanFields.objects.get(id=boolean_page.id)
    >>> for field in boolean_page._meta.fields:
    ...     print field.name, field.value_to_string(boolean_page)
    id 1
    boolean_field True
    null_boolean_field None


Now for each field, we will test both creation and modification of the value.

Boolean
~~~~~~~
::

    >>> page = RemotePageWithBooleanFields.objects.create(boolean_field=True)
    >>> page.boolean_field
    True
    >>> page = RemotePageWithBooleanFields.objects.get(id=page.id)
    >>> page.boolean_field
    True
    >>> page.boolean_field = False
    >>> page.save()
    >>> page = RemotePageWithBooleanFields.objects.get(id=page.id)
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

    >>> page = RemotePageWithManyFields.objects.create(email_field=u"roa_user@example.com")
    >>> page.email_field
    u'roa_user@example.com'
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.email_field
    u'roa_user@example.com'
    >>> page.email_field = u"roa_user@example.org"
    >>> page.save()
    >>> page = RemotePageWithManyFields.objects.get(id=page.id)
    >>> page.email_field
    u'roa_user@example.org'
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

NullBoolean
~~~~~~~~~~~
::

    >>> page = RemotePageWithBooleanFields.objects.create(null_boolean_field=True)
    >>> page.null_boolean_field
    True
    >>> page = RemotePageWithBooleanFields.objects.get(id=page.id)
    >>> page.null_boolean_field
    True
    >>> page.null_boolean_field = False
    >>> page.save()
    >>> page = RemotePageWithBooleanFields.objects.get(id=page.id)
    >>> page.null_boolean_field
    False
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


Relations
---------

First things first, we verify that default attributes are set to ``None`` or
empty values even when it comes from the server::

    >>> from django_roa_client.models import RemotePageWithRelations
    >>> default_page = RemotePageWithRelations.objects.create()
    >>> for field in default_page._meta.fields:
    ...     print field.name, field.value_to_string(default_page)
    id 1
    title 
    remote_page None
    >>> default_page = RemotePageWithRelations.objects.get(id=default_page.id)
    >>> for field in default_page._meta.fields:
    ...     print field.name, field.value_to_string(default_page)
    id 1
    title 
    remote_page None


ForeignKey
~~~~~~~~~~~
::

    >>> remote_page = RemotePage.objects.create(title=u"A remote page")
    >>> another_remote_page = RemotePage.objects.create(title=u"Another remote page")
    >>> page = RemotePageWithRelations.objects.create(remote_page=remote_page)
    >>> page.remote_page
    <RemotePage: A remote page (1)>
    >>> page = RemotePageWithRelations.objects.get(id=page.id)
    >>> page.remote_page
    <RemotePage: A remote page (1)>
    >>> page.remote_page = another_remote_page
    >>> page.save()
    >>> page = RemotePageWithRelations.objects.get(id=page.id)
    >>> page.remote_page
    <RemotePage: Another remote page (2)>
    >>> page.delete()
    >>> remote_page.delete()
    >>> another_remote_page.delete()

ManyToMany
~~~~~~~~~~
::

    >>> remote_page = RemotePageWithManyFields.objects.create(char_field=u"A remote page")
    >>> another_remote_page = RemotePageWithManyFields.objects.create(char_field=u"Another remote page")
    >>> page = RemotePageWithRelations.objects.create(title=u"A remote relation page")
    >>> page.remote_page_fields.add(remote_page)
    >>> page.remote_page_fields.all()
    [<RemotePageWithManyFields: RemotePageWithManyFields (1)>]
    >>> page = RemotePageWithRelations.objects.get(id=page.id)
    >>> page.remote_page_fields.all()
    [<RemotePageWithManyFields: RemotePageWithManyFields (1)>]
    >>> page.remote_page_fields.add(another_remote_page)
    >>> page = RemotePageWithRelations.objects.get(id=page.id)
    >>> page.remote_page_fields.all()
    [<RemotePageWithManyFields: RemotePageWithManyFields (1)>, <RemotePageWithManyFields: RemotePageWithManyFields (2)>]
    >>> remote_page.remotepagewithrelations_set.all()
    [<RemotePageWithRelations: A remote relation page (2)>]
    >>> page.remote_page_fields.remove(remote_page)
    >>> page.remote_page_fields.all()
    [<RemotePageWithManyFields: RemotePageWithManyFields (2)>]
    >>> page.remote_page_fields.clear()
    >>> page.remote_page_fields.all()
    []
    >>> page.delete()
    >>> remote_page.delete()
    >>> another_remote_page.delete()


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

    >>> from django_roa.remoteauth.models import User, Message
    >>> User.objects.all()
    [<User: roa_user>]
    >>> alice = User.objects.create_user(username="alice", password="secret", email="alice@example.com")
    >>> alice.is_superuser
    False
    >>> User.objects.all()
    [<User: roa_user>, <User: alice>]
    >>> alice.id
    2
    >>> Message.objects.all()
    []
    >>> message = Message.objects.create(user=alice, message=u"Test message")
    >>> message.message
    u'Test message'
    >>> message.user
    <User: alice>
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
    >>> User.objects.create_superuser(username="bob", password="secret", email="bob@example.com")
    <User: bob>
    >>> bob = User.objects.get(username="bob")
    >>> bob.is_superuser
    True
    >>> c.login(username="bob", password="secret")
    True
    >>> response = c.get("/admin/")
    >>> response.context[-1]["user"]
    <User: bob>
    >>> response = c.get("/admin/django_roa_client/remotepage/")
    >>> response.status_code
    200
    >>> response.context[-1]["cl"].result_list
    [<RemotePage: A fool remote page (5)>, <RemotePage: A fourth remote page (4)>]
    >>> response.context[-1]["cl"].result_count
    5


Forms
-----

We verify that Forms' validation works as expected::

    >>> from django_roa_client.forms import TestForm
    >>> form = TestForm()
    >>> form.is_valid()
    False
    >>> rp = RemotePage.objects.all()[0]
    >>> form = TestForm(data={u'test_field': u'Test data', u'remote_page': rp.id})
    >>> form.is_valid()
    True
    
Same verification with ModelForms::

    >>> from django_roa_client.forms import RemotePageForm
    >>> form = RemotePageForm()
    >>> form.is_valid()
    False
    >>> form = RemotePageForm(data={u'title': u'Test data'})
    >>> form.is_valid()
    True
    >>> remote_page = form.save()
    >>> remote_page
    <RemotePage: Test data (6)>
    >>> remote_page.delete()


Home
----

Test the rendering of a ModelForm with complex relations (depends on
previously created remote pages)::

    >>> c = Client()
    >>> response = c.get('/')
    >>> print response.content
    <li><label for="id_title">Title:</label> <input id="id_title" type="text" name="title" maxlength="50" /></li>
    <li><label for="id_remote_page">Remote page:</label> <select name="remote_page" id="id_remote_page">
    <option value="" selected="selected">---------</option>
    <option value="1">A second remote page (1)</option>
    <option value="2">A third remote page (2)</option>
    <option value="3">A fourth remote page (3)</option>
    <option value="4">A fourth remote page (4)</option>
    <option value="5">A fool remote page (5)</option>
    </select></li>
    <li><label for="id_remote_page_fields">Remote page fields:</label> <select multiple="multiple" name="remote_page_fields" id="id_remote_page_fields">
    </select>  Hold down "Control", or "Command" on a Mac, to select more than one.</li>


Groups & Permissions
--------------------

As with users, there are remote groups and permissions::

    >>> from django.contrib.contenttypes.models import ContentType
    >>> from django_roa.remoteauth.models import Group, Permission
    >>> Permission.objects.all()
    [...]
    >>> Permission.objects.all().delete()
    >>> bob.user_permissions.all()
    []
    >>> ct_user = ContentType.objects.get(name='user')
    >>> user_permission = Permission.objects.create(name=u"Custom permission to user model",
    ...                                        content_type=ct_user,
    ...                                        codename=u"custom_user_permission")
    >>> bob.user_permissions.add(user_permission)
    >>> bob.user_permissions.all()
    [<Permission: remoteauth | user | Custom permission to user model>]

    >>> Group.objects.all()
    []
    >>> bob.groups.all()
    []
    >>> ct_group = ContentType.objects.get(name='group')
    >>> group_permission = Permission.objects.create(name=u"Custom permission to group model",
    ...                                              content_type=ct_group,
    ...                                              codename=u"custom_group_permission")
    >>> group = Group.objects.create(name=u"Custom group")
    >>> group.permissions.add(group_permission)
    >>> bob.groups.add(group)
    >>> bob.groups.all()
    [<Group: Custom group>]
    >>> bob.groups.all()[0].permissions.all()
    [<Permission: remoteauth | group | Custom permission to group model>]
    
    >>> alice.get_group_permissions()
    set([])
    >>> bob.get_group_permissions()
    set([u'remoteauth.custom_group_permission'])
    >>> bob.get_all_permissions()
    set([u'remoteauth.custom_group_permission', u'remoteauth.custom_user_permission'])


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

    >>> User.objects.create_user(username="alice", password="secret", email="alice@example.com")
    Traceback (most recent call last):
    ...
    ROAException: IntegrityError at /auth/user/: column username is not unique
     Request Method: POST
     Request URL: http://127.0.0.1:8081/auth/user/?format=django
     Exception Type: IntegrityError
     Exception Value: column username is not unique
     Exception Location: ..., line ...
     Status code: 500


Custom serializer
-----------------

You can use your own serializer thanks to the ``SERIALIZATION_MODULES`` Django
setting (registered manually here for test purpose)::

    >>> from django.conf import settings
    >>> initial_roa_format_setting = settings.ROA_FORMAT
    >>> from django.core.serializers import register_serializer
    >>> register_serializer('custom', 'examples.django_roa_client.serializers')
    >>> settings.ROA_FORMAT = 'custom'
    >>> page = RemotePage.objects.create(title=u'A custom serialized page')
    >>> page
    <RemotePage: A custom serialized page (6)>
    >>> from restclient import RestClient
    >>> rc = RestClient()
    >>> response = rc.get('http://127.0.0.1:8081/django_roa_server/remotepage/?format=custom')
    >>> print response
    <?xml version="1.0" encoding="utf-8"?>
    <django-test version="1.0">
     <object pk="1" model="django_roa_server.remotepage">
      <field type="CharField" name="title">A second remote page</field>
     </object>
     ...
    </django-test>
    
    >>> len(RemotePage.objects.all())
    6
    >>> page = RemotePage.objects.get(id=page.id)
    >>> page
    <RemotePage: A custom serialized page (6)>
    >>> page.delete()
    >>> settings.ROA_FORMAT = initial_roa_format_setting


Custom extra arguments
----------------------
::

    >>> initial_roa_custom_arg_setting = getattr(settings, 'ROA_CUSTOM_ARGS', {})
    >>> settings.ROA_CUSTOM_ARGS = {'foo': 'bar'}
    >>> RemotePage.objects.all()._as_url()
    (u'http://127.0.0.1:8081/django_roa_server/remotepage/', {'foo': 'bar', 'format': 'django'})
    >>> settings.ROA_CUSTOM_ARGS = initial_roa_custom_arg_setting


Clean up
--------
::

    >>> RemotePage.objects.all().delete()
    >>> RemotePageWithManyFields.objects.all().delete()
    >>> RemotePageWithBooleanFields.objects.all().delete()
    >>> RemotePageWithRelations.objects.all().delete()
    >>> RemotePageWithCustomSlug.objects.all().delete()
    >>> RemotePageWithOverriddenUrls.objects.all().delete()
    >>> User.objects.exclude(username="roa_user").delete()
    >>> Permission.objects.all().delete()
    >>> Group.objects.all().delete()

"""
