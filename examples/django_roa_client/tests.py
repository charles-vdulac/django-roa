# -*- coding: utf-8 -*-
r"""
Unit tests for django-roa.

These tests assume that you've completed all the prerequisites for
getting django-roa running in the default setup, to wit:

1.  You have created the remote database: go to ``examples/django_roa_server``
    and run ``syncdb`` command with ``--noinput`` option in order to create
    a superuser named "roa_user" from fixtures:

        $ python manage.py syncdb --noinput

2.  You have launched the project's server on port 8081 in order to test this
    suite against it with this command:

        $ python manage.py runserver 8081

Now, you can go to ``examples/django_roa_client`` and run this command:

    $ python manage.py test django_roa_client

It should return no error and you will be able to see logs from the test
server which confirm that it works as expected: remote requests are done.

Note: do not try to launch tests' projects if you put ``django_roa``
application into your own project, otherwise it will fail. Django do not
handle very well projects inside projects.
"""
from datetime import time, date, datetime

from django.test import TestCase
from django.conf import settings
from django.test.client import Client
from django.core.serializers import register_serializer
from django.contrib.contenttypes.models import ContentType

from restkit import Resource
from django_roa.remoteauth.models import User, Message, Group, Permission
from django_roa_client.models import RemotePage, RemotePageWithManyFields, \
    RemotePageWithBooleanFields, RemotePageWithRelations, \
    RemotePageWithCustomSlug, RemotePageWithOverriddenUrls, \
    RemotePageWithNamedRelations, RemotePageWithProxy, \
    RemotePageWithRelationsThrough, RemotePageWithCustomPrimaryKey, \
    RemotePageWithCustomPrimaryKeyCountOverridden
from django_roa_client.forms import TestForm, RemotePageForm
from django_roa.db.exceptions import ROAException

ROA_FILTERS = getattr(settings, 'ROA_FILTERS', {})

class ROATestCase(TestCase):

    def setUp(self):
        RemotePage.objects.all().delete()
        RemotePageWithCustomPrimaryKey.objects.all().delete()

    def tearDown(self):
        RemotePage.objects.all().delete()
        RemotePageWithCustomPrimaryKey.objects.all().delete()

class ROAUserTestCase(ROATestCase):

    def setUp(self):
        super(ROAUserTestCase, self).setUp()
        User.objects.all().delete()
        self.user = User.objects.create_superuser('admin', 'admin@example.org', 'admin')

    def tearDown(self):
        super(ROAUserTestCase, self).tearDown()
        User.objects.all().delete()
        Message.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()


class ROAInitializationTests(ROATestCase):

    def test_inheritance(self):
        self.assertEqual(str(RemotePage.objects.__class__), "<class 'django_roa.db.managers.ROAManager'>")
        self.assertEqual(str(RemotePage.__class__), "<class 'django_roa.db.models.ROAModelBase'>")


class ROABaseTests(ROATestCase):

    def test_basic_crud(self):
        page = RemotePage.objects.create(title=u'A first remote page')
        self.assertEqual(repr(page), '<RemotePage: A first remote page (1)>')
        page.title = u'Another title'
        page.save()
        page = RemotePage.objects.get(title=u'Another title')
        self.assertEqual(page.title, u'Another title')
        pages = RemotePage.objects.all()
        self.assertEqual(repr(pages), '[<RemotePage: Another title (1)>]')
        page.delete()
        self.assertEqual(repr(RemotePage.objects.all()), '[]')
        # test custom mapping of arguments too
        self.assertEqual(RemotePage.objects.count(), 0)

    def test_complex_crud(self):
        page = RemotePage.objects.create(title=u'')
        self.assertEqual(page.title, u'')
        page.title = u'A temporary title'
        page.save()
        page = RemotePage.objects.get(title=u'A temporary title')
        self.assertEqual(page.title, u'A temporary title')
        self.assertEqual(RemotePage.objects.count(), 1)
        page.title = u''
        page.save()
        page = RemotePage.objects.all()[0]
        self.assertEqual(page.title, u'')
        page.delete()
        self.assertEqual(repr(RemotePage.objects.all()), '[]')
        self.assertEqual(RemotePage.objects.count(), 0)


class ROAUnicodeTests(ROATestCase):

    def test_remotepage(self):
        emilie = RemotePage.objects.create(title=u"Émilie")
        self.assertEqual(emilie.title, u'Émilie')
        emilie = RemotePage.objects.get(title=u"Émilie")
        self.assertEqual(emilie.title, u'Émilie')
        amelie = emilie
        amelie.title = u'Amélie'
        amelie.save()
        self.assertEqual(amelie.title, u'Amélie')
        amelie = RemotePage.objects.get(title=u"Amélie")
        self.assertEqual(amelie.title, u'Amélie')
        amelie.delete()


class ROAFieldsTests(ROATestCase):

    def tearDown(self):
        super(ROAFieldsTests, self).tearDown()
        RemotePageWithManyFields.objects.all().delete()
        RemotePageWithBooleanFields.objects.all().delete()

    def test_empty_values(self):
        default_page = RemotePageWithManyFields.objects.create()
        self.assertEqual(default_page.id, 1)
        self.assertEqual(default_page.char_field, None)
        self.assertEqual(default_page.date_field, None)
        self.assertEqual(default_page.datetime_field, None)
        self.assertEqual(default_page.decimal_field, None)
        self.assertEqual(default_page.email_field, None)
        self.assertEqual(default_page.filepath_field, None)
        self.assertEqual(default_page.float_field, None)
        self.assertEqual(default_page.integer_field, None)
        self.assertEqual(default_page.ipaddress_field, None)
        self.assertEqual(default_page.positiveinteger_field, None)
        self.assertEqual(default_page.positivesmallinteger_field, None)
        self.assertEqual(default_page.slug_field, None)
        self.assertEqual(default_page.smallinteger_field, None)
        self.assertEqual(default_page.text_field, None)
        self.assertEqual(default_page.time_field, None)
        self.assertEqual(default_page.url_field, None)
        self.assertEqual(default_page.xml_field, None)
        self.assertEqual(repr(default_page.file_field), '<FieldFile: None>')
        self.assertEqual(repr(default_page.image_field), '<ImageFieldFile: None>')
        retrieved_default_page = RemotePageWithManyFields.objects.get(id=default_page.id)
        self.assertEqual(default_page.id, retrieved_default_page.id)
        self.assertEqual(default_page.char_field, retrieved_default_page.char_field)
        self.assertEqual(default_page.date_field, retrieved_default_page.date_field)
        self.assertEqual(default_page.datetime_field, retrieved_default_page.datetime_field)
        self.assertEqual(default_page.decimal_field, retrieved_default_page.decimal_field)
        self.assertEqual(default_page.email_field, retrieved_default_page.email_field)
        self.assertEqual(default_page.filepath_field, retrieved_default_page.filepath_field)
        self.assertEqual(default_page.float_field, retrieved_default_page.float_field)
        self.assertEqual(default_page.integer_field, retrieved_default_page.integer_field)
        self.assertEqual(default_page.ipaddress_field, retrieved_default_page.ipaddress_field)
        self.assertEqual(default_page.positiveinteger_field, retrieved_default_page.positiveinteger_field)
        self.assertEqual(default_page.positivesmallinteger_field, retrieved_default_page.positivesmallinteger_field)
        self.assertEqual(default_page.slug_field, retrieved_default_page.slug_field)
        self.assertEqual(default_page.smallinteger_field, retrieved_default_page.smallinteger_field)
        self.assertEqual(default_page.text_field, retrieved_default_page.text_field)
        self.assertEqual(default_page.time_field, retrieved_default_page.time_field)
        self.assertEqual(default_page.url_field, retrieved_default_page.url_field)
        self.assertEqual(default_page.xml_field, retrieved_default_page.xml_field)
        self.assertEqual(repr(default_page.file_field), repr(retrieved_default_page.file_field))
        self.assertEqual(repr(default_page.image_field), repr(retrieved_default_page.image_field))
        default_page.delete()

    def test_empty_boolean_values(self):
        boolean_page = RemotePageWithBooleanFields.objects.create(boolean_field=True)
        self.assertEqual(boolean_page.id, 1)
        self.assertEqual(boolean_page.boolean_field, True)
        self.assertEqual(boolean_page.null_boolean_field, None)
        retrieved_boolean_page = RemotePageWithBooleanFields.objects.get(id=boolean_page.id)
        self.assertEqual(boolean_page.id, retrieved_boolean_page.id)
        self.assertEqual(boolean_page.boolean_field, retrieved_boolean_page.boolean_field)
        self.assertEqual(boolean_page.null_boolean_field, retrieved_boolean_page.null_boolean_field)
        boolean_page.delete()

    def test_boolean_field(self):
        page = RemotePageWithBooleanFields.objects.create(boolean_field=True)
        self.assertEqual(page.boolean_field, True)
        page = RemotePageWithBooleanFields.objects.get(id=page.id)
        self.assertEqual(page.boolean_field, True)
        page.boolean_field = False
        page.save()
        page = RemotePageWithBooleanFields.objects.get(id=page.id)
        self.assertEqual(page.boolean_field, False)
        page.delete()

    def test_char_field(self):
        page = RemotePageWithManyFields.objects.create(char_field=u'foo')
        self.assertEqual(page.char_field, u'foo')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.char_field, u'foo')
        page.char_field = u'bar'
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.char_field, u'bar')
        page.delete()

    def test_date_field(self):
        page = RemotePageWithManyFields.objects.create(date_field=date(2008, 12, 24))
        self.assertEqual(repr(page.date_field), 'datetime.date(2008, 12, 24)')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.date_field), 'datetime.date(2008, 12, 24)')
        page.date_field = date(2008, 12, 25)
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.date_field), 'datetime.date(2008, 12, 25)')
        page.delete()

    def test_datetime_field(self):
        page = RemotePageWithManyFields.objects.create(datetime_field=datetime(2008, 12, 24, 11, 53, 57))
        self.assertEqual(repr(page.datetime_field), 'datetime.datetime(2008, 12, 24, 11, 53, 57)')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.datetime_field), 'datetime.datetime(2008, 12, 24, 11, 53, 57)')
        page.datetime_field = datetime(2008, 12, 25, 13, 20)
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.datetime_field), 'datetime.datetime(2008, 12, 25, 13, 20)')
        page.delete()

    def test_decimal_field(self):
        page = RemotePageWithManyFields.objects.create(decimal_field=1.55)
        self.assertEqual(page.decimal_field, 1.55)
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.decimal_field), "Decimal('1.55')")
        page.decimal_field = 20.09
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.decimal_field), "Decimal('20.09')")
        page.delete()

    def test_email_field(self):
        page = RemotePageWithManyFields.objects.create(email_field=u'test@example.com')
        self.assertEqual(page.email_field, u'test@example.com')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.email_field, u'test@example.com')
        page.email_field = u'test@example.org'
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.email_field, u'test@example.org')
        page.delete()

    def test_filepath_field(self):
        page = RemotePageWithManyFields.objects.create(filepath_field=u'/foo/bar.zip')
        self.assertEqual(page.filepath_field, u'/foo/bar.zip')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.filepath_field, u'/foo/bar.zip')
        page.filepath_field = u'/foo/bar/baz.tar.gz'
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.filepath_field, u'/foo/bar/baz.tar.gz')
        page.delete()

    def test_float_field(self):
        page = RemotePageWithManyFields.objects.create(float_field=1.55)
        self.assertEqual(page.float_field, 1.55)
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.float_field, 1.55)
        page.float_field = 20.09
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.float_field, 20.09)
        page.delete()

    def test_integer_field(self):
        page = RemotePageWithManyFields.objects.create(integer_field=155)
        self.assertEqual(page.integer_field, 155)
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.integer_field, 155)
        page.integer_field = 2009
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.integer_field, 2009)
        page.delete()

    def test_nullboolean_field(self):
        page = RemotePageWithBooleanFields.objects.create(null_boolean_field=True)
        self.assertEqual(page.null_boolean_field, True)
        page = RemotePageWithBooleanFields.objects.get(id=page.id)
        self.assertEqual(page.null_boolean_field, True)
        page.null_boolean_field = False
        page.save()
        page = RemotePageWithBooleanFields.objects.get(id=page.id)
        self.assertEqual(page.null_boolean_field, False)
        page.delete()

    def test_slug_field(self):
        page = RemotePageWithManyFields.objects.create(slug_field=u'foo-bar')
        self.assertEqual(page.slug_field, u'foo-bar')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.slug_field, u'foo-bar')
        page.slug_field = u'bar-baz'
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.slug_field, u'bar-baz')
        page.delete()

    def test_text_field(self):
        page = RemotePageWithManyFields.objects.create(text_field=u'foo bar')
        self.assertEqual(page.text_field, u'foo bar')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.text_field, u'foo bar')
        page.text_field = u'foo bar\nbaz'
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.text_field, u'foo bar\nbaz')
        page.delete()

    def test_time_field(self):
        page = RemotePageWithManyFields.objects.create(time_field=time(3, 51, 28))
        self.assertEqual(repr(page.time_field), 'datetime.time(3, 51, 28)')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.time_field), 'datetime.time(3, 51, 28)')
        page.time_field = time(11, 20, 53)
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(repr(page.time_field), 'datetime.time(11, 20, 53)')
        page.delete()

    def test_url_field(self):
        page = RemotePageWithManyFields.objects.create(url_field=u'http://example.com')
        self.assertEqual(page.url_field, u'http://example.com')
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.url_field, u'http://example.com')
        page.url_field = u'http://example.org'
        page.save()
        page = RemotePageWithManyFields.objects.get(id=page.id)
        self.assertEqual(page.url_field, u'http://example.org')
        page.delete()


class ROARelationsTests(ROATestCase):

    def tearDown(self):
        super(ROARelationsTests, self).tearDown()
        RemotePageWithManyFields.objects.all().delete()
        RemotePageWithRelations.objects.all().delete()
        RemotePageWithNamedRelations.objects.all().delete()

    def test_empty_relation(self):
        relations_page = RemotePageWithRelations.objects.create()
        self.assertEqual(relations_page.id, 1)
        self.assertEqual(relations_page.title, '')
        self.assertEqual(relations_page.remote_page, None)
        retrieved_relations_page = RemotePageWithRelations.objects.get(id=relations_page.id)
        self.assertEqual(relations_page.id, retrieved_relations_page.id)
        self.assertEqual(relations_page.title, retrieved_relations_page.title)
        self.assertEqual(relations_page.remote_page, retrieved_relations_page.remote_page)
        relations_page.delete()

    def test_foreignkey_relation(self):
        remote_page = RemotePage.objects.create(title=u'A remote page')
        another_remote_page = RemotePage.objects.create(title=u'Another remote page')
        relations_page = RemotePageWithRelations.objects.create(remote_page=remote_page)
        self.assertEqual(repr(relations_page.remote_page), '<RemotePage: A remote page (1)>')
        relations_page = RemotePageWithRelations.objects.get(id=relations_page.id)
        self.assertEqual(repr(relations_page.remote_page), '<RemotePage: A remote page (1)>')
        self.assertEqual(repr(remote_page.remotepagewithrelations_set.all()), '[<RemotePageWithRelations:  (1)>]')
        relations_page.remote_page = another_remote_page
        relations_page.save()
        relations_page = RemotePageWithRelations.objects.get(id=relations_page.id)
        self.assertEqual(repr(relations_page.remote_page), '<RemotePage: Another remote page (2)>')
        relations_page.delete()
        another_remote_page.delete()
        remote_page.delete()

    def test_manytomany_relation(self):
        remote_page = RemotePageWithManyFields.objects.create(char_field=u'A remote page')
        another_remote_page = RemotePageWithManyFields.objects.create(char_field=u'Another remote page')
        relations_page = RemotePageWithRelations.objects.create(title=u'A remote relation page')
        relations_page_through = RemotePageWithRelationsThrough.objects.create(title=u'A remote relation page through',
                                                                               remote_page_with_relations=relations_page,
                                                                               remote_page_with_many_fields=remote_page)
        self.assertEqual(repr(relations_page.remote_page_fields.all()), '[<RemotePageWithManyFields: RemotePageWithManyFields (1)>]')
        relations_page = RemotePageWithRelations.objects.get(id=relations_page.id)
        self.assertEqual(repr(relations_page.remote_page_fields.all()), '[<RemotePageWithManyFields: RemotePageWithManyFields (1)>]')
        another_relations_page_through = RemotePageWithRelationsThrough.objects.create(title=u'Another remote relation page through',
                                                                                       remote_page_with_relations=relations_page,
                                                                                       remote_page_with_many_fields=another_remote_page)
        relations_page = RemotePageWithRelations.objects.get(id=relations_page.id)
        self.assertEqual(repr(relations_page.remote_page_fields.all()), '[<RemotePageWithManyFields: RemotePageWithManyFields (1)>, <RemotePageWithManyFields: RemotePageWithManyFields (2)>]')
        self.assertEqual(repr(remote_page.remotepagewithrelations_set.all()), '[<RemotePageWithRelations: A remote relation page (1)>]')
        relations_page_through.delete()
        self.assertEqual(repr(relations_page.remote_page_fields.all()), '[<RemotePageWithManyFields: RemotePageWithManyFields (2)>]')
        another_relations_page_through.delete()
        self.assertEqual(repr(relations_page.remote_page_fields.all()), '[]')
        relations_page.delete()
        another_remote_page.delete()
        remote_page.delete()

    def test_named_relation(self):
        remote_page = RemotePage.objects.create(title=u'A remote page')
        another_remote_page = RemotePage.objects.create(title=u'Another remote page')
        named_relations_page = RemotePageWithNamedRelations.objects.create(first_page=remote_page,
                                                                           last_page=another_remote_page)
        self.assertEqual(repr(named_relations_page.first_page), '<RemotePage: A remote page (1)>')
        named_relations_page = RemotePageWithNamedRelations.objects.get(id=named_relations_page.id)
        self.assertEqual(repr(named_relations_page.first_page), '<RemotePage: A remote page (1)>')
        self.assertEqual(repr(remote_page.from_first.all()), '[<RemotePageWithNamedRelations:  (1)>]')
        self.assertEqual(repr(another_remote_page.from_last.all()), '[<RemotePageWithNamedRelations:  (1)>]')
        named_relations_page.first_page = another_remote_page
        named_relations_page.save()
        named_relations_page = RemotePageWithNamedRelations.objects.get(id=named_relations_page.id)
        self.assertEqual(repr(named_relations_page.first_page), '<RemotePage: Another remote page (2)>')
        named_relations_page.delete()
        another_remote_page.delete()
        remote_page.delete()

    def test_proxy_relation(self):
        remote_page = RemotePage.objects.create(title=u'A remote page')
        proxy_remote_page = RemotePageWithProxy.objects.create(title=u'A proxy remote page')
        self.assertEqual(repr(remote_page), '<RemotePage: A remote page (1)>')
        self.assertEqual(repr(proxy_remote_page), '<RemotePageWithProxy: A proxy remote page (2)>')
        self.assertEqual(repr(RemotePage.objects.all()), '[<RemotePage: A remote page (1)>, <RemotePage: A proxy remote page (2)>]')
        self.assertEqual(repr(RemotePageWithProxy.objects.all()), '[<RemotePage: A remote page (1)>, <RemotePage: A proxy remote page (2)>]')
        proxy_remote_page.title = u'A modified proxy remote page'
        proxy_remote_page.save()
        proxy_remote_page = RemotePageWithProxy.objects.get(id=2)
        self.assertEqual(repr(proxy_remote_page), '<RemotePage: A modified proxy remote page (2)>')
        self.assertEqual(repr(RemotePage.objects.all()[1]), '<RemotePage: A modified proxy remote page (2)>')
        proxy_remote_page.delete()
        remote_page.delete()


class ROAQuerysetTests(ROATestCase):

    def setUp(self):
        super(ROAQuerysetTests, self).setUp()
        self.remote_page1 = RemotePage.objects.create(title='A remote page')
        self.remote_page2 = RemotePage.objects.create(title='Another remote page')
        self.remote_page3 = RemotePage.objects.create(title='Yet another remote page')
        self.remote_page4 = RemotePage.objects.create(title='Still another remote page')
        self.remote_page_with_custom_primary_key1 = RemotePageWithCustomPrimaryKey.objects.create(title=u'Remote test page with custom primary')
        self.remote_page_with_custom_primary_key2 = RemotePageWithCustomPrimaryKey.objects.create(title=u'Another remote test page with custom primary')

    def test_getorcreate(self):
        self.assertEqual(repr(RemotePage.objects.get_or_create(title='A remote page')), '(<RemotePage: A remote page (1)>, False)')
        remote_page, created = RemotePage.objects.get_or_create(title='A created remote page')
        self.assertEqual(created, True)

    def test_latest(self):
        self.assertEqual(repr(RemotePage.objects.latest('id')), '<RemotePage: Still another remote page (4)>')
        self.assertEqual(repr(RemotePage.objects.latest('title')), '<RemotePage: Yet another remote page (3)>')

    def test_filtering(self):
        self.assertEqual(repr(RemotePage.objects.exclude(id=2)), '[<RemotePage: A remote page (1)>, <RemotePage: Yet another remote page (3)>, <RemotePage: Still another remote page (4)>]')
        self.assertEqual(repr(RemotePage.objects.filter(title__iexact='ANOTHER remote page')), '[<RemotePage: Another remote page (2)>]')
        self.assertEqual(repr(RemotePage.objects.filter(title__contains='another')), '[<RemotePage: Another remote page (2)>, <RemotePage: Yet another remote page (3)>, <RemotePage: Still another remote page (4)>]')

    def test_ordering(self):
        self.assertEqual(repr(RemotePage.objects.order_by('title')), '[<RemotePage: A remote page (1)>, <RemotePage: Another remote page (2)>, <RemotePage: Still another remote page (4)>, <RemotePage: Yet another remote page (3)>]')
        self.assertEqual(repr(RemotePage.objects.order_by('-title', '-id')), '[<RemotePage: Yet another remote page (3)>, <RemotePage: Still another remote page (4)>, <RemotePage: Another remote page (2)>, <RemotePage: A remote page (1)>]')

    def test_slicing(self):
        self.assertEqual(repr(RemotePage.objects.all()[1:3]), '[<RemotePage: Another remote page (2)>, <RemotePage: Yet another remote page (3)>]')
        self.assertEqual(repr(RemotePage.objects.all()[0]), '<RemotePage: A remote page (1)>')

    def test_extra(self):
        self.assertEqual(bool(RemotePage.objects.all().extra(select={'a': 1}).values('a').order_by()), True)
        RemotePage.objects.all().delete()
        self.assertEqual(bool(RemotePage.objects.all().extra(select={'a': 1}).values('a').order_by()), False)

    def test_combined(self):
        self.assertEqual(repr(RemotePage.objects.exclude(title__contains='yet').order_by('title', '-id')[:2]), '[<RemotePage: A remote page (1)>, <RemotePage: Another remote page (2)>]')

    def test_get(self):
        # test get by pk, id directly
        self.assertEqual(repr(RemotePage.objects.get(id=1)), '<RemotePage: A remote page (1)>')
        self.assertEqual(repr(RemotePage.objects.get(pk=2)), '<RemotePage: Another remote page (2)>')
        # test get by pk, id with exact filter
        self.assertEqual(repr(RemotePage.objects.get(id__exact=3)), '<RemotePage: Yet another remote page (3)>')
        self.assertEqual(repr(RemotePage.objects.get(pk__exact=4)), '<RemotePage: Still another remote page (4)>')

        # test get by custom primary key attribute name
        self.assertEqual(repr(RemotePageWithCustomPrimaryKey.objects.get(auto_field=1)), '<RemotePageWithCustomPrimaryKey: Remote test page with custom primary (1)>')
        self.assertEqual(repr(RemotePageWithCustomPrimaryKey.objects.get(auto_field=2)), '<RemotePageWithCustomPrimaryKey: Another remote test page with custom primary (2)>')
        with self.assertRaisesRegexp(ROAException, 'Not Found'):
            RemotePageWithCustomPrimaryKey.objects.get(auto_field=999)

        # test get by custom primary key with exact filter
        self.assertEqual(repr(RemotePageWithCustomPrimaryKey.objects.get(auto_field__exact=1)), '<RemotePageWithCustomPrimaryKey: Remote test page with custom primary (1)>')
        self.assertEqual(repr(RemotePageWithCustomPrimaryKey.objects.get(auto_field__exact=2)), '<RemotePageWithCustomPrimaryKey: Another remote test page with custom primary (2)>')
        with self.assertRaisesRegexp(ROAException, 'Not Found'):
            RemotePageWithCustomPrimaryKey.objects.get(auto_field__exact=999)

        # test get by multiple attributes
        self.assertEqual(repr(RemotePageWithCustomPrimaryKey.objects.get(title='Another remote test page with custom primary', auto_field=2)), '<RemotePageWithCustomPrimaryKey: Another remote test page with custom primary (2)>')
        self.assertEqual(repr(RemotePageWithCustomPrimaryKey.objects.get(title__exact='Another remote test page with custom primary', auto_field__exact=2)), '<RemotePageWithCustomPrimaryKey: Another remote test page with custom primary (2)>')
        with self.assertRaisesRegexp(ROAException, 'Not Found'):
            RemotePageWithCustomPrimaryKey.objects.get(title__exact='Another remote test page with custom primary', auto_field__exact=999)

    def test_count(self):
        self.assertEqual(RemotePageWithCustomPrimaryKey.objects.count(), 2)
        RemotePageWithCustomPrimaryKey.objects.all().delete()
        self.assertEqual(RemotePageWithCustomPrimaryKey.objects.count(), 0)

        RemotePageWithCustomPrimaryKey.objects.create(title=u'Remote test page with custom primary')
        self.assertEqual(RemotePageWithCustomPrimaryKeyCountOverridden.objects.count(), 0)

class ROAAdminTests(ROAUserTestCase):

    def test_admin_views(self):
        remote_page1 = RemotePage.objects.create(title='A remote page')
        remote_page2 = RemotePage.objects.create(title='Another remote page')
        remote_page3 = RemotePage.objects.create(title='Yet another remote page')
        remote_page4 = RemotePage.objects.create(title='Still another remote page')
        bob = User.objects.create_superuser(username=u'bob', password=u'secret', email=u'bob@example.com')
        bob = User.objects.get(username=u'bob')
        self.assertEqual(bob.is_superuser, True)
        c = Client()
        response = c.login(username=u'bob', password=u'secret')
        self.assertEqual(response, True)
        response = c.get('/admin/')
        # ._wrapped necessary because we compare string, comparison should
        # work with User.objects.get(username="bob") but slower...
        self.assertEqual(repr(response.context[-1]["user"]._wrapped), '<User: bob>')
        response = c.get('/admin/django_roa_client/remotepage/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repr(response.context[-1]["cl"].result_list), '[<RemotePage: Still another remote page (4)>, <RemotePage: Yet another remote page (3)>]')
        self.assertEqual(response.context[-1]["cl"].result_count, 4)


class ROAFormsTests(ROATestCase):

    def test_form_validation(self):
        form = TestForm()
        remote_page1 = RemotePage.objects.create(title='A remote page')
        self.assertEqual(form.is_valid(), False)
        form = TestForm(data={u'test_field': u'Test data', u'remote_page': remote_page1.id})
        self.assertEqual(form.is_valid(), True)

    def test_modelform_validation(self):
        form = RemotePageForm()
        self.assertEqual(form.is_valid(), False)
        form = RemotePageForm(data={u'title': u'Test data'})
        self.assertEqual(form.is_valid(), True)
        remote_page = form.save()
        self.assertEqual(repr(remote_page), '<RemotePage: Test data (1)>')

    def test_modelform_rendering(self):
        c = Client()
        remote_page1 = RemotePage.objects.create(title='A remote page')
        response = c.get('/')
        self.assertEqual('<select name="remote_page" id="id_remote_page">\n<option value="" selected="selected">---------</option>\n<option value="1">A remote page (1)</option>\n</select>' in response.content, True)


class ROARemoteAuthTests(ROAUserTestCase):

    def test_remote_users(self):
        self.assertEqual(repr(User.objects.all()), '[<User: admin>]')
        alice = User.objects.create_user(username=u'alice', password=u'secret', email=u'alice@example.com')
        self.assertEqual(alice.is_superuser, False)
        self.assertEqual(repr(User.objects.all()), '[<User: admin>, <User: alice>]')
        self.assertEqual(alice.id, 2)
        self.assertEqual(repr(Message.objects.all()), '[]')
        message = Message.objects.create(user=alice, message=u'Test message')
        self.assertEqual(message.message, u'Test message')
        self.assertEqual(repr(message.user), '<User: alice>')
        self.assertEqual(repr(Message.objects.all()), '[<Message: Test message>]')
        self.assertEqual(repr(alice.message_set.all()), '[<Message: Test message>]')

    def test_select_related(self):
        # Not supported, we just verify that it doesn't break anything
        alice = User.objects.create_user(username=u'alice', password=u'secret', email=u'alice@example.com')
        message = Message.objects.create(user=alice, message=u'Test message')
        self.assertEqual(repr(Message.objects.all().select_related()), '[<Message: Test message>]')
        self.assertEqual(repr(Message.objects.all().select_related('user')), '[<Message: Test message>]')

    def test_groups(self):
        bob = User.objects.create_superuser(username=u'bob', password=u'secret', email=u'bob@example.com')
        self.assertEqual(repr(Group.objects.all()), '[]')
        self.assertEqual(repr(bob.groups.all()), '[]')
        ct_group = ContentType.objects.get(name='group')
        group_permission = Permission.objects.create(name=u"Custom permission to group model",
                                                     content_type=ct_group,
                                                     codename=u"custom_group_permission")
        group = Group.objects.create(name=u"Custom group")
        #group.permissions.add(group_permission)
        #bob.groups.add(group)
        #self.assertEqual(repr(bob.groups.all()), '[<Group: Custom group>]')
        #self.assertEqual(repr(bob.groups.all()[0].permissions.all()), '[<Permission: remoteauth | group | Custom permission to group model>]')
        self.assertEqual(repr(bob.groups.all()), '[]')

    def test_permissions(self):
        bob = User.objects.create_superuser(username=u'bob', password=u'secret', email=u'bob@example.com')
        self.assertEqual(repr(bob.user_permissions.all()), '[]')
        ct_user = ContentType.objects.get(name='user')
        user_permission = Permission.objects.create(name=u"Custom permission to user model",
                                                    content_type=ct_user,
                                                    codename=u"custom_user_permission")
        #bob.user_permissions.add(user_permission)
        #self.assertEqual(repr(bob.user_permissions.all()), '[<Permission: remoteauth | user | Custom permission to user model>]')
        self.assertEqual(repr(bob.user_permissions.all()), '[]')
        ct_group = ContentType.objects.get(name='group')
        group_permission = Permission.objects.create(name=u"Custom permission to group model",
                                                     content_type=ct_group,
                                                     codename=u"custom_group_permission")
        group = Group.objects.create(name=u"Custom group")
        #group.permissions.add(group_permission)
        #bob.groups.add(group)
        #self.assertEqual(bob.get_group_permissions(), set([u'remoteauth.custom_group_permission']))
        #self.assertEqual(bob.get_all_permissions(), set([u'remoteauth.custom_group_permission', u'remoteauth.custom_user_permission']))
        self.assertEqual(bob.get_group_permissions(), set([]))
        self.assertEqual(bob.get_all_permissions(), set([]))


class ROAExceptionsTests(ROAUserTestCase):

    def test_roa_errors(self):
        """
        FIXME: Find a way to do the same test with unittests:

        > User.objects.create_user(username="alice", password="secret", email="alice@example.com")
        Traceback (most recent call last):
        ...
        ROAException: IntegrityError at /auth/user/: column username is not unique
         Request Method: POST
         Request URL: http://127.0.0.1:8081/auth/user/?format=django
         Exception Type: IntegrityError
         Exception Value: column username is not unique
         Exception Location: ..., line ...
         Status code: 500
        """
        User.objects.create_user(username="alice", password="secret", email="alice@example.com")
        #User.objects.create_user(username="alice", password="secret", email="alice@example.com")


class ROASettingsTests(ROATestCase):

    def tearDown(self):
        super(ROASettingsTests, self).tearDown()
        RemotePageWithCustomSlug.objects.all().delete()
        RemotePageWithOverriddenUrls.objects.all().delete()

    def test_custom_args(self):
        settings.ROA_CUSTOM_ARGS = {'foo': 'bar'}
        self.assertEqual(RemotePage.objects.all()._as_url(), (u'http://127.0.0.1:8081/django_roa_server/remotepage/', {'foo': 'bar', 'format': 'django'}))
        settings.ROA_CUSTOM_ARGS = {}

    def test_custom_slug(self):
        page_custom = RemotePageWithCustomSlug.objects.create(title=u"Test custom page")
        self.assertEqual(page_custom.slug, u'test-custom-page')
        page_custom = RemotePageWithCustomSlug.objects.get(title=u"Test custom page")
        self.assertEqual(repr(page_custom), '<RemotePageWithCustomSlug: Test custom page (1)>')
        page_custom.delete()

    def test_roa_url_overrides(self):
        page_overridden = RemotePageWithOverriddenUrls.objects.create(title=u"Test overridden urls")
        self.assertEqual(page_overridden.slug, u'test-overridden-urls')
        page_overridden = RemotePageWithOverriddenUrls.objects.get(title=u"Test overridden urls")
        self.assertEqual(repr(page_overridden), '<RemotePageWithOverriddenUrls: Test overridden urls (1)>')
        self.assertEqual(RemotePageWithOverriddenUrls.objects.all()._as_url(), (u'http://127.0.0.1:8081/django_roa_server/remotepagewithoverriddenurls/', {'format': 'django'}))

    def test_custom_serializer(self):
        register_serializer('custom', 'examples.django_roa_client.serializers')
        initial_roa_format_setting = settings.ROA_FORMAT
        settings.ROA_FORMAT = 'custom'
        page = RemotePage.objects.create(title=u'A custom serialized page')
        self.assertEqual(repr(page), '<RemotePage: A custom serialized page (1)>')
        r = Resource('http://127.0.0.1:8081/django_roa_server/remotepage/', filters=ROA_FILTERS)
        response = r.get(**{'format': 'custom'})
        self.assertEqual(repr(response.body_string()), '\'<?xml version="1.0" encoding="utf-8"?>\\n<django-test version="1.0">\\n <object pk="1" model="django_roa_server.remotepage">\\n  <field type="CharField" name="title">A custom serialized page</field>\\n </object>\\n</django-test>\'')
        self.assertEqual(len(RemotePage.objects.all()), 1)
        page = RemotePage.objects.get(id=page.id)
        self.assertEqual(repr(page), '<RemotePage: A custom serialized page (1)>')
        settings.ROA_FORMAT = initial_roa_format_setting
