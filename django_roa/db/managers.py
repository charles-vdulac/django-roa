from django.db.models.manager import Manager

from django_roa.db.query import RemoteQuerySet


class RemoteManager(Manager):
    """
    Manager which access remote resources.
    """
    use_for_related_fields = True
    
    def get_query_set(self):
        """
        Returns a QuerySet which access remote resources.
        """
        return RemoteQuerySet(self.model)
