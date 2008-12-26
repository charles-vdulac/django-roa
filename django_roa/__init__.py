# Depends on settings for flexibility
from django.conf import settings
from django.db.models import Model
from django.db.models.manager import Manager

from django_roa.db.models import RemoteModel
from django_roa.db.managers import RemoteManager

Model = getattr(settings, "ROA_MODELS", False) and RemoteModel or Model
Manager = getattr(settings, "ROA_MODELS", False) and RemoteManager or Manager
