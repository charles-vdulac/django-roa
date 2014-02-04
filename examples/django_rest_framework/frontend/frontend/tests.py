from rest_framework.test import APITestCase
from .models import Account, Article, Tag, Reporter


class ROATestCase(APITestCase):

    def test_get(self):

        # Get
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
        # TODO:
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
