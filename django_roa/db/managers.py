from django.db.models.manager import Manager as DjangoManager

from django_roa.db.query import RemoteQuerySet


class RemoteManager(DjangoManager):
    """
    Manager which access remote resources.
    """
    use_for_related_fields = True
    
    def get_query_set(self):
        """
        Returns a QuerySet which access remote resources.
        """
        return RemoteQuerySet(self.model)
