import logging
from django_roa.remoteauth.models import User
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from restkit import BasicAuth


logger = logging.getLogger("django_roa")


# API authentication
#
# There are 2 different ways:
#
# - constant auth: API requires authentication which does not depend on the connected user (User):
#   You just have to set ROA_FILTERS. For example, ROA_FILTERS = [BasicAuth('username', 'password')]
#
# - API requires authentication depending on the user logged:
#   You have to set ROA_API_REQUIRE_AUTH to True, then set ROA_API_AUTH_KIND and perhaps ROA_API_AUTH_DEFAULT_ACCOUNT.
#   ROA_API_AUTH_DEFAULT_ACCOUNT is useful if an authentication must be provided when user is not connected.
#   If ROA_API_AUTH_DEFAULT_ACCOUNT, you have to set ROA_FILTERS too.
#   ROA_API_AUTH_KIND: for now, only 'basic' (BasicAuth). Please refer to restkit filters


ROA_API_REQUIRE_AUTH = getattr(settings, 'ROA_API_REQUIRE_AUTH', False)  # auth required ?
ROA_API_AUTH_KIND = getattr(settings, 'ROA_API_AUTH_KIND', 'basic')  # which type of authentication ?
ROA_API_AUTH_DEFAULT_ACCOUNT = getattr(settings, 'ROA_API_AUTH_DEFAULT_ACCOUNT', {})  # default authentication params


def set_api_auth(username, password, kind=None):
    """
    Authenticates consumer to API
    """
    if not ROA_API_REQUIRE_AUTH:
        return

    kind = kind or ROA_API_AUTH_KIND
    logger.debug(u"Set {} API auth login".format(kind))

    if kind == 'basic':
        reset_api_auth(kind, logging=False)
        settings.ROA_FILTERS.append(BasicAuth(username, password))
    else:
        raise Exception(u'ROA: Unsupported auth kind: {}'.format(kind))


def reset_api_auth(kind=None, auth_default_account=None, logging=True):
    """
    Consumer API logout.
    You can have a default auth account
    """
    if not ROA_API_REQUIRE_AUTH:
        return

    kind = kind or ROA_API_AUTH_KIND
    auth_default_account = auth_default_account or ROA_API_AUTH_DEFAULT_ACCOUNT

    if logging:
        logger.debug(u"Reset {} API auth login".format(kind))

    if kind == 'basic':
        # clean
        for item in settings.ROA_FILTERS:
            if type(item) != BasicAuth:
                continue
            else:
                settings.ROA_FILTERS.remove(item)
        # set default auth:
        if auth_default_account:
            settings.ROA_FILTERS.append(BasicAuth(auth_default_account['username'], auth_default_account['password']))
    else:
        raise Exception(u'ROA: Unsupported auth kind: {}'.format(kind))


class RemoteUserModelBackend(ModelBackend):
    """
    Authenticates against django_roa.remoteauth.models.RemoteUser.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                set_api_auth(user.username, password)
                user._password = password  # save password for future use
                return user
        except User.DoesNotExist:
            reset_api_auth()
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
            reset_api_auth()
            return None
