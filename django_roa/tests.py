r"""
==========
Django ROA
==========

Tests
=====

How to run tests
----------------

You need to launch ``test_projects/django_roa_server`` project on port 8081 in 
order to test this suite with this command::

    $ python manage.py runserver 8081

Then you can go to ``test_projects/django_roa_client`` and run this command::

    $ python manage.py test

It should return no error and you will be able to see logs from the test
server which confirm that it works as expected: remote requests are done.

Initialization
--------------

First of all, we verify that remote classes are called::

    >>> from django_roa_client.models import RemotePage
    >>> RemotePage.objects.__class__
    <class 'django_roa.db.managers.RemoteManager'>
    >>> RemotePage.__class__
    <class 'django_roa.db.models.ResourceAsMetaModelBase'>

API
---

Now, let's create, update, retrieve and delete a simple object::

    >>> page = RemotePage.objects.create(title='A first remote page')
    >>> page
    <RemotePage: A first remote page (1)>
    >>> page.title = 'Another title'
    >>> page.save()
    >>> page = RemotePage.objects.get(title='Another title') # from cache (TODO!)
    >>> page.title
    u'Another title'
    >>> pages = RemotePage.objects.all()
    >>> pages
    [<RemotePage: Another title (1)>]
    >>> pages.count() # do not hit the remote web service (from cache)
    1
    >>> page.delete()
    >>> RemotePage.objects.all()
    []
    >>> RemotePage.objects.count() # hit the remote web service
    0

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


Users
-----

Remote users are defined in ``django_roa.remoteauth`` application::

    >>> from django_roa.remoteauth.models import RemoteUser, RemoteMessage
    >>> RemoteUser.objects.all()
    [<RemoteUser: david>]
    >>> alice = RemoteUser.objects.create_user(username="alice", password="secret", email="alice@example.com")
    >>> alice.is_superuser
    False
    >>> RemoteUser.objects.all()
    [<RemoteUser: david>, <RemoteUser: alice>]
    >>> alice.id
    2
    >>> RemoteMessage.objects.all()
    []
    >>> message = RemoteMessage.objects.create(user=alice, message=u"Test message")
    >>> message.message
    u'Test message'
    >>> message.user
    <RemoteUser: alice>
    >>> RemoteMessage.objects.all()
    [<RemoteMessage: Test message>]
    >>> #alice.remotemessage_set.all()


Clean up
--------
::

    >>> RemotePage.objects.all().delete()
    >>> RemoteUser.objects.exclude(username="david").delete()
"""
