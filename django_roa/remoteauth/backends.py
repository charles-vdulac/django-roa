from django.contrib.auth.backends import ModelBackend

from django_roa.remoteauth.models import RemoteUser

class RemoteUserModelBackend(ModelBackend):
    """
    Authenticates against django_roa.remoteauth.models.RemoteUser.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = RemoteUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except RemoteUser.DoesNotExist:
            return None

    def get_group_permissions(self, user_obj):
        """
        Returns a set of permission strings that this user has through his/her
        groups.
        """
        if not hasattr(user_obj, '_group_perm_cache'):
            #cursor = connection.cursor()
            #qn = connection.ops.quote_name
            #sql = """
            #    SELECT ct.%s, p.%s
            #    FROM %s p, %s gp, %s ug, %s ct
            #    WHERE p.%s = gp.%s
            #        AND gp.%s = ug.%s
            #        AND ct.%s = p.%s
            #        AND ug.%s = %%s""" % (
            #    qn('app_label'), qn('codename'),
            #    qn('auth_permission'), qn('auth_group_permissions'),
            #    qn('auth_user_groups'), qn('django_content_type'),
            #    qn('id'), qn('permission_id'),
            #    qn('group_id'), qn('group_id'),
            #    qn('id'), qn('content_type_id'),
            #    qn('user_id'),)
            #cursor.execute(sql, [user_obj.id])
            #user_obj._group_perm_cache = set(["%s.%s" % (row[0], row[1]) for row in cursor.fetchall()])
            # TODO: get permissions for remote models
            user_obj._group_perm_cache = []
        return user_obj._group_perm_cache

    def get_user(self, user_id):
        try:
            return RemoteUser.objects.get(pk=user_id)
        except RemoteUser.DoesNotExist:
            return None
