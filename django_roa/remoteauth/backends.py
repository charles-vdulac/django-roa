from django.contrib.auth.backends import ModelBackend

from django_roa.remoteauth.models import User

class RemoteUserModelBackend(ModelBackend):
    """
    Authenticates against django_roa.remoteauth.models.RemoteUser.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_group_permissions(self, user_obj):
        """
        Returns a set of permission strings that this user has through his/her
        groups.
        """
        if not hasattr(user_obj, '_group_perm_cache'):
            # TODO: improve performances
            permissions = [u"%s.%s" % (p.content_type.app_label, p.codename) \
                                        for group in user_obj.groups.all() \
                                            for p in group.permissions.all()]
            user_obj._group_perm_cache = permissions
        return user_obj._group_perm_cache

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
