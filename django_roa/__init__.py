# Depends on settings for flexibility
from django.conf import settings
from django.db.models import signals, Model as DjangoModel
from django.db.models.manager import Manager as DjangoManager
from django.db.models.fields import FieldDoesNotExist

from django_roa.db.models import ROAModel
from django_roa.db.managers import ROAManager

ROA_MODELS = getattr(settings, "ROA_MODELS", False)
Model = ROA_MODELS and ROAModel or DjangoModel
Manager = ROA_MODELS and ROAManager or DjangoManager

def ensure_roa_manager(sender, **kwargs):
    cls = sender
    manager = getattr(cls, '_default_manager', None)
    if (not manager and not cls._meta.abstract) \
            or (ROA_MODELS and hasattr(cls, 'get_resource_url_list') \
                and not hasattr(manager, 'is_roa_manager')):
        # Create the default manager, if needed.
        cls.add_to_class('objects', Manager())
        cls.add_to_class('_default_manager', Manager())

signals.class_prepared.connect(ensure_roa_manager)

