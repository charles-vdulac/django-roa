from rest_framework import routers
from .api.views import AccountViewSet, ReporterViewSet, ArticleViewSet, \
    TagViewSet, ReversedArticleViewSet, ReversedReporterViewSet, \
    ReversedTagViewSet, ReversedAccountViewSet


# API
router = routers.DefaultRouter()
router.register(r'accounts', AccountViewSet, base_name='account')
router.register(r'reporters', ReporterViewSet, base_name='reporter')
router.register(r'articles', ArticleViewSet, base_name='article')
router.register(r'tags', TagViewSet, base_name='tag')
router.register(r'reversed/tags', ReversedTagViewSet, base_name='reversedtag')
router.register(r'reversed/articles', ReversedArticleViewSet, base_name='reversedarticle')
router.register(r'reversed/reporters', ReversedReporterViewSet, base_name='reversedreporter')
router.register(r'reversed/accounts', ReversedAccountViewSet, base_name='reversedaccount')

urlpatterns = router.urls
