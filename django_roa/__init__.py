# Depends on settings for flexibility
from django.conf import settings

from django_roa.db.models import RemoteModel, DjangoModel
from django_roa.db.managers import RemoteManager, DjangoManager

Model = getattr(settings, "ROA_MODELS", False) and RemoteModel or DjangoModel
Manager = getattr(settings, "ROA_MODELS", False) and RemoteManager or DjangoManager
