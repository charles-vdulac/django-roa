from django.utils.timezone import now
from rest_framework.test import APITestCase
from django_roa.db.exceptions import ROAException
from .models import Account, Article, Tag, Reporter


class ROATestCase(APITestCase):

    def test_all(self):

        #
        # Get
        #

        account = Account.objects.get(id=1)
        self.assertEqual(account.id, 1)
        self.assertEqual(account.email, 'john@example.com')

        account = Account.objects.get(email='paul@example.com')
        self.assertEqual(account.id, 2)
        self.assertEqual(account.email, 'paul@example.com')

        # All
        accounts = Account.objects.all()
        self.assertEqual(accounts.count(), 2)
        self.assertEqual(accounts[0].id, 1)
        self.assertEqual(accounts[0].email, 'john@example.com')
        self.assertEqual(accounts[1].id, 2)
        self.assertEqual(accounts[1].email, 'paul@example.com')

        # filter
        accounts = Account.objects.filter(email='paul@example.com')
        self.assertEqual(accounts.count(), 1)
        self.assertEqual(accounts[0].id, 2)
        self.assertEqual(accounts[0].email, 'paul@example.com')

        #
        # Relationships
        # Typical relationships applications
        #

        # One to One
        reporter = Reporter.objects.get(id=1)
        self.assertEqual(reporter.first_name, "John")
        self.assertEqual(reporter.account.id, 1)
        self.assertEqual(reporter.account.email, 'john@example.com')

        # One to one reversed:
        # TODO: doesn't work
        # account = Account.objects.get(id=1)
        # self.assertEqual(account.reporter.id, 1)
        # self.assertEqual(account.reporter.first_name, "John")

        # One to Many
        articles = reporter.articles.all()
        self.assertEqual(articles.count(), 2)
        self.assertEqual(articles[0].id, 1)
        self.assertEqual(articles[0].headline, "John's first story")
        self.assertEqual(articles[1].id, 2)
        self.assertEqual(articles[1].headline, "John's second story")

        # Many to one
        article = Article.objects.get(id=1)
        self.assertEqual(article.reporter.id, 1)
        self.assertEqual(article.reporter.first_name, "John")

        # Many to Many
        tags = articles[0].tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertEqual(tags[0].id, 1)
        self.assertEqual(tags[0].label, 'news')
        self.assertEqual(tags[1].id, 2)
        self.assertEqual(tags[1].label, 'january')

        # Many to Many reversed
        tag = Tag.objects.get(id=1)
        self.assertEqual(tag.label, 'news')
        articles = tag.articles.all()
        self.assertEqual(articles.count(), 3)
        self.assertEqual(articles[0].id, 1)
        self.assertEqual(articles[0].headline, "John's first story")
        self.assertEqual(articles[1].id, 2)
        self.assertEqual(articles[1].headline, "John's second story")
        self.assertEqual(articles[2].id, 3)
        self.assertEqual(articles[2].headline, "Paul's story")

        #
        # Create
        #

        new_account = Account()
        new_account.email = 'peter@example.com'
        new_account.save()

        self.assertIsNotNone(new_account.id)

        accounts = Account.objects.all()
        self.assertEqual(accounts.count(), 3)
        self.assertEqual(accounts[0].email, 'john@example.com')
        self.assertEqual(accounts[1].email, 'paul@example.com')
        self.assertEqual(accounts[2].email, 'peter@example.com')

        #
        # Delete
        #

        new_account.delete()
        self.assertIsNone(new_account.pk)

        accounts = Account.objects.all()
        self.assertEqual(accounts.count(), 2)

        #
        # Create with relationship
        #

        count_accounts = Account.objects.count()
        count_reporters = Reporter.objects.count()
        count_articles = Article.objects.count()

        new_account = Account()
        new_account.email = 'james@example.com'
        new_account.save()

        new_reporter = Reporter()
        new_reporter.account = new_account
        new_reporter.first_name = 'James'
        new_reporter.last_name = 'Doe'
        new_reporter.save()

        new_article = Article()
        new_article.headline = "James's story"
        new_article.reporter = new_reporter
        self.assertRaises(ROAException, new_article.save)  # pub_date is required
        new_article.pub_date = now().date()
        new_article.save()

        # There are 3 lines where new_account is save:
        # new_account.save()
        # new_reporter.save()
        # new_article.save()
        # But only one instance must be save into db.
        # TODO: goal: only one record.
        self.assertEqual(Account.objects.count(), count_accounts + 3)
        # Same case:
        self.assertEqual(Reporter.objects.count(), count_reporters + 2)
        self.assertEqual(Article.objects.count(), count_articles + 1)

        article = Article.objects.get(headline="James's story")
        self.assertEqual(article.reporter.first_name, 'James')
        self.assertEqual(article.reporter.account.email, 'james@example.com')


    def test_empty_list_no_pagination(self):
        tags = Tag.objects.filter(label='idonetexist')

        # To check that iterating over the empty queryset works
        for i in tags:
            pass

        self.assertEqual(tags.count(), 0)
