from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

from django_roa.remoteauth.models import RemoteUser

class RemoteUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = RemoteUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except RemoteUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return RemoteUser.objects.get(pk=user_id)
        except RemoteUser.DoesNotExist:
            return None
