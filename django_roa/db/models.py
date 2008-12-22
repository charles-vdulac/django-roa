import sys
from django.conf import settings
from django.db import models, connection, transaction
from django.db.models import signals
from django.db.models.fields import AutoField
from django.core import serializers

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldError
from django.db.models.fields import AutoField
from django.db.models.fields.related import OneToOneRel, ManyToOneRel, OneToOneField
from django.db.models.query import delete_objects, Q, CollectedObjects
from django.db.models.options import Options
from django.db.models import signals, Manager
from django.db.models.loading import register_models, get_model
from django.db.models.base import ModelBase, subclass_exception

from restclient import Resource
from django_roa.db.managers import RemoteManager

class ResourceAsMetaModelBase(ModelBase):
    """
    Deal with the new Meta ``resource_url_list`` attribute in __new__.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        # Create the class.
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        attr_meta = attrs.pop('Meta', None)
        abstract = getattr(attr_meta, 'abstract', False)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, '_meta', None)

        if getattr(meta, 'app_label', None) is None:
            # Figure out the app_label by looking one level up.
            # For 'django.contrib.sites.models', this would be 'sites'.
            model_module = sys.modules[new_class.__module__]
            kwargs = {"app_label": model_module.__name__.split('.')[-2]}
        else:
            kwargs = {}

        # Custom Meta, replace:
        # new_class.add_to_class('_meta', Options(meta, **kwargs))
        resource_url_list = None
        options = Options(meta, **kwargs)
        if hasattr(options, 'meta') and options.meta is not None:
            resource_url_list = options.meta.__dict__['resource_url_list']
            del options.meta.__dict__['resource_url_list']
        new_class.add_to_class('_meta', options)
        if resource_url_list is not None:
            setattr(new_class._meta, 'resource_url_list', resource_url_list)
        # /Custom Meta

        if not abstract:
            new_class.add_to_class('DoesNotExist',
                    subclass_exception('DoesNotExist', ObjectDoesNotExist, module))
            new_class.add_to_class('MultipleObjectsReturned',
                    subclass_exception('MultipleObjectsReturned', MultipleObjectsReturned, module))
            if base_meta and not base_meta.abstract:
                # Non-abstract child classes inherit some attributes from their
                # non-abstract parent (unless an ABC comes before it in the
                # method resolution order).
                if not hasattr(meta, 'ordering'):
                    new_class._meta.ordering = base_meta.ordering
                if not hasattr(meta, 'get_latest_by'):
                    new_class._meta.get_latest_by = base_meta.get_latest_by

        # Custom default manager (sometimes Django instanciate a classic one?)
        #if getattr(new_class, '_default_manager', None):
        #    new_class._default_manager = None
        new_class._default_manager = RemoteManager()
        new_class._default_manager.contribute_to_class(new_class, name)
        # /Custom default manager

        # Bail out early if we have already created this class.
        m = get_model(new_class._meta.app_label, name, False)
        if m is not None:
            return m

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # Do the appropriate setup for any model parents.
        o2o_map = dict([(f.rel.to, f) for f in new_class._meta.local_fields
                if isinstance(f, OneToOneField)])
        for base in parents:
            if not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue

            # All the fields of any type declared on this model
            new_fields = new_class._meta.local_fields + \
                         new_class._meta.local_many_to_many + \
                         new_class._meta.virtual_fields
            field_names = set([f.name for f in new_fields])

            if not base._meta.abstract:
                # Concrete classes...
                if base in o2o_map:
                    field = o2o_map[base]
                    field.primary_key = True
                    new_class._meta.setup_pk(field)
                else:
                    attr_name = '%s_ptr' % base._meta.module_name
                    field = OneToOneField(base, name=attr_name,
                            auto_created=True, parent_link=True)
                    new_class.add_to_class(attr_name, field)
                new_class._meta.parents[base] = field

            else:
                # .. and abstract ones.

                # Check for clashes between locally declared fields and those
                # on the ABC.
                parent_fields = base._meta.local_fields + base._meta.local_many_to_many
                for field in parent_fields:
                    if field.name in field_names:
                        raise FieldError('Local field %r in class %r clashes '\
                                         'with field of similar name from '\
                                         'abstract base class %r' % \
                                            (field.name, name, base.__name__))
                    new_class.add_to_class(field.name, copy.deepcopy(field))

                # Pass any non-abstract parent classes onto child.
                new_class._meta.parents.update(base._meta.parents)

            # Inherit managers from the abstract base classes.
            base_managers = base._meta.abstract_managers
            base_managers.sort()
            for _, mgr_name, manager in base_managers:
                val = getattr(new_class, mgr_name, None)
                if not val or val is manager:
                    new_manager = manager._copy_to_model(new_class)
                    new_class.add_to_class(mgr_name, new_manager)

            # Inherit virtual fields (like GenericForeignKey) from the parent class
            for field in base._meta.virtual_fields:
                if base._meta.abstract and field.name in field_names:
                    raise FieldError('Local field %r in class %r clashes '\
                                     'with field of similar name from '\
                                     'abstract base class %r' % \
                                        (field.name, name, base.__name__))
                new_class.add_to_class(field.name, copy.deepcopy(field))

        if abstract:
            # Abstract base models can't be instantiated and don't appear in
            # the list of models for an app. We do the final setup for them a
            # little differently from normal models.
            attr_meta.abstract = False
            new_class.Meta = attr_meta
            return new_class

        new_class._prepare()
        register_models(new_class._meta.app_label, new_class)

        # Because of the way imports happen (recursively), we may or may not be
        # the first time this model tries to register with the framework. There
        # should only be one class for each model, so we always return the
        # registered version.
        return get_model(new_class._meta.app_label, name, False)


class RemoteModel(models.Model):
    """
    Model which access remote resources.
    """
    __metaclass__ = ResourceAsMetaModelBase
    
    @property
    def resource_url_detail(self):
        return u"%s%s/" % (self._meta.resource_url_list, self.pk)
    
    def save_base(self, raw=False, cls=None, force_insert=False,
            force_update=False):
        assert not (force_insert and force_update)
        if not cls:
            cls = self.__class__
            meta = self._meta
            signal = True
            signals.pre_save.send(sender=self.__class__, instance=self, raw=raw)
        else:
            meta = cls._meta
            signal = False
        
        # If we are in a raw save, save the object exactly as presented.
        # That means that we don't try to be smart about saving attributes
        # that might have come from the parent class - we just save the
        # attributes we have been given to the class we have been given.
        if not raw:
            for parent, field in meta.parents.items():
                # At this point, parent's primary key field may be unknown
                # (for example, from administration form which doesn't fill
                # this field). If so, fill it.
                if getattr(self, parent._meta.pk.attname) is None and getattr(self, field.attname) is not None:
                    setattr(self, parent._meta.pk.attname, getattr(self, field.attname))
                
                #self.save_base(raw, parent)
                setattr(self, field.attname, self._get_pk_val(parent._meta))

        non_pks = [f for f in meta.local_fields if not f.primary_key]

        args = dict((field.name, field.value_to_string(self)) for field in meta.local_fields)
        fk_args = dict((field.get_attname(), getattr(self, field.name).id) \
                    for field in meta.local_fields \
                        if isinstance(field, models.ForeignKey) \
                            and field.name != 'remotemodel_ptr')
        args.update(fk_args)
        pk_val = self._get_pk_val(meta)
        pk_set = pk_val is not None

        if force_update or pk_set and not self.id is None:
            resource = Resource(self.resource_url_detail)
            response = resource.put(**args)
        else:
            resource = Resource(meta.resource_url_list)
            response = resource.post(**args)
        
        result = serializers.deserialize(getattr(settings, "ROA_FORMAT", 'json'), response).next()

        try:
            result_id = int(result.object.remotemodel_ptr_id)
        except AttributeError: # FK
            result_id = int(result.object.id)
        self.id = self.remotemodel_ptr_id = result_id
        self = result.object

    save_base.alters_data = True

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)

        # TODO: Find all the objects that need to be deleted.
        resource = Resource(self.resource_url_detail)
        response = resource.delete()

    delete.alters_data = True


class DjangoModel(models.Model):
    """
    Model which allows ``resource_url_list`` as Meta attribute.
    """
    __metaclass__ = ResourceAsMetaModelBase
    

