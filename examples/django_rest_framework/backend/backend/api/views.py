from .mixins import ModelViewSet
from .models import Account, Reporter, Article, Tag
from .serializers import AccountSerializer, ReporterSerializer, ArticleSerializer, \
    TagSerializer, ReversedReporterSerializer, ReversedArticleSerializer, \
    ReversedTagSerializer, ReversedAccountSerializer


# Filters and permissions are declared in settings


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class ReporterViewSet(ModelViewSet):
    queryset = Reporter.objects.all()
    serializer_class = ReporterSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# Reversed


class ReversedTagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = ReversedTagSerializer


class ReversedArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ReversedArticleSerializer


class ReversedReporterViewSet(ModelViewSet):
    queryset = Reporter.objects.all()
    serializer_class = ReversedReporterSerializer


class ReversedAccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = ReversedAccountSerializer
