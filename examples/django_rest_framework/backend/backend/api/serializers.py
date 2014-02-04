from rest_framework import serializers
from .models import Account, Reporter, Article, Tag


#
# Model serializers
# Typical relationships applications
#


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'email')


class ReporterSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    class Meta:
        model = Reporter
        fields = ('id', 'account', 'first_name', 'last_name')


class ArticleSerializer(serializers.ModelSerializer):
    reporter = ReporterSerializer()
    class Meta:
        model = Article
        fields = ('id', 'headline', 'pub_date', 'reporter')


class TagSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True)
    class Meta:
        model = Tag
        fields = ('id', 'label', 'articles')


#
# Model serializers
# Reversed relationships applications
#


class ReversedTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'label')


class ReversedArticleSerializer(serializers.ModelSerializer):
    tags = ReversedTagSerializer(many=True)
    class Meta:
        model = Article
        fields = ('id', 'headline', 'pub_date', 'tags')


class ReversedReporterSerializer(serializers.ModelSerializer):
    articles = ReversedArticleSerializer()

    class Meta:
        model = Reporter
        fields = ('id', 'first_name', 'last_name', 'articles')


class ReversedAccountSerializer(serializers.ModelSerializer):
    reporter = ReversedReporterSerializer()
    class Meta:
        model = Account
        fields = ('id', 'email', 'reporter')

