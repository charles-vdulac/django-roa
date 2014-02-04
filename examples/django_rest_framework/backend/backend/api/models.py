from django.db import models


# Declare a model with all relationships


class Account(models.Model):
    email = models.CharField(max_length=30)


class Reporter(models.Model):
    account = models.OneToOneField(Account, related_name='reporter')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(Reporter, related_name='articles')


class Tag(models.Model):
    label = models.CharField(max_length=30)
    articles = models.ManyToManyField(Article, related_name='tags')
