import sys
import copy
import logging

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned,\
    FieldError
from django.db import models
from django.db.models import signals
from django.db.models.options import Options
from django.db.models.loading import register_models, get_model
from django.db.models.base import ModelBase, subclass_exception, \
    get_absolute_url, method_get_order, method_set_order
from django.db.models.fields.related import OneToOneField
from django.utils.functional import curry, update_wrapper
from django.utils.encoding import force_unicode, smart_unicode

from restkit import Resource, RequestFailed
from django_roa.db.exceptions import ROAException

logger = logging.getLogger("django_roa")

ROA_MODEL_NAME_MAPPING = getattr(settings, 'ROA_MODEL_NAME_MAPPING', [])
ROA_HEADERS = getattr(settings, 'ROA_HEADERS', {})
ROA_FORMAT = getattr(settings, 'ROA_FORMAT', 'json')
ROA_FILTERS = getattr(settings, 'ROA_FILTERS', {})

DEFAULT_CHARSET = getattr(settings, 'DEFAULT_CHARSET', 'utf-8')

class ROAModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        """
        Exactly the same except the line with ``isinstance(b, ROAModelBase)``.
        """
        super_new = super(ModelBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ROAModelBase)]
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

        new_class.add_to_class('_meta', Options(meta, **kwargs))
        if not abstract:
            new_class.add_to_class('DoesNotExist', subclass_exception('DoesNotExist',
                    tuple(x.DoesNotExist
                            for x in parents if hasattr(x, '_meta') and not x._meta.abstract)
                                    or (ObjectDoesNotExist,), module))
            new_class.add_to_class('MultipleObjectsReturned', subclass_exception('MultipleObjectsReturned',
                    tuple(x.MultipleObjectsReturned
                            for x in parents if hasattr(x, '_meta') and not x._meta.abstract)
                                    or (MultipleObjectsReturned,), module))
            if base_meta and not base_meta.abstract:
                # Non-abstract child classes inherit some attributes from their
                # non-abstract parent (unless an ABC comes before it in the
                # method resolution order).
                if not hasattr(meta, 'ordering'):
                    new_class._meta.ordering = base_meta.ordering
                if not hasattr(meta, 'get_latest_by'):
                    new_class._meta.get_latest_by = base_meta.get_latest_by

        is_proxy = new_class._meta.proxy

        if getattr(new_class, '_default_manager', None):
            if not is_proxy:
                # Multi-table inheritance doesn't inherit default manager from
                # parents.
                new_class._default_manager = None
                new_class._base_manager = None
            else:
                # Proxy classes do inherit parent's default manager, if none is
                # set explicitly.
                new_class._default_manager = \
                        new_class._default_manager._copy_to_model(new_class)
                new_class._base_manager = \
                        new_class._base_manager._copy_to_model(new_class)

        # Bail out early if we have already created this class.
        m = get_model(new_class._meta.app_label, name, False)
        if m is not None:
            return m

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        # All the fields of any type declared on this model
        new_fields = new_class._meta.local_fields + \
                     new_class._meta.local_many_to_many + \
                     new_class._meta.virtual_fields
        field_names = set([f.name for f in new_fields])

        # Basic setup for proxy models.
        if is_proxy:
            base = None
            for parent in [cls for cls in parents if hasattr(cls, '_meta')]:
                if parent._meta.abstract:
                    if parent._meta.fields:
                        raise TypeError("Abstract base class containing model "\
                                        "fields not permitted for proxy model '%s'." % name)
                    else:
                        continue
                if base is not None:
                    raise TypeError("Proxy model '%s' has more than one " \
                                    "non-abstract model base class." % name)
                else:
                    base = parent
            if base is None:
                    raise TypeError("Proxy model '%s' has no non-abstract " \
                                    "model base class." % name)
            if (new_class._meta.local_fields or
                    new_class._meta.local_many_to_many):
                raise FieldError("Proxy model '%s' contains model fields."
                        % name)
            while base._meta.proxy:
                base = base._meta.proxy_for_model
            new_class._meta.setup_proxy(base)

        # Do the appropriate setup for any model parents.
        o2o_map = dict([(f.rel.to, f) for f in new_class._meta.local_fields
                if isinstance(f, OneToOneField)])

        for base in parents:
            original_base = base
            if not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue

            parent_fields = base._meta.local_fields + base._meta.local_many_to_many
            # Check for clashes between locally declared fields and those
            # on the base classes (we cannot handle shadowed fields at the
            # moment).
            for field in parent_fields:
                if field.name in field_names:
                    raise FieldError('Local field %r in class %r clashes '
                                     'with field of similar name from '
                                     'base class %r' %
                                        (field.name, name, base.__name__))
            if not base._meta.abstract:
                # Concrete classes...
                while base._meta.proxy:
                    # Skip over a proxy class to the "real" base it proxies.
                    base = base._meta.proxy_for_model
                if base in o2o_map:
                    field = o2o_map[base]
                elif not is_proxy:
                    attr_name = '%s_ptr' % base._meta.module_name
                    field = OneToOneField(base, name=attr_name,
                            auto_created=True, parent_link=True)
                    new_class.add_to_class(attr_name, field)
                else:
                    field = None
                new_class._meta.parents[base] = field
            else:
                # .. and abstract ones.
                for field in parent_fields:
                    new_class.add_to_class(field.name, copy.deepcopy(field))

                # Pass any non-abstract parent classes onto child.
                new_class._meta.parents.update(base._meta.parents)

            # Inherit managers from the abstract base classes.
            new_class.copy_managers(base._meta.abstract_managers)

            # Proxy models inherit the non-abstract managers from their base,
            # unless they have redefined any of them.
            if is_proxy:
                new_class.copy_managers(original_base._meta.concrete_managers)

            # Inherit virtual fields (like GenericForeignKey) from the parent
            # class
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

    def _prepare(cls):
        """
        Creates some methods once self._meta has been populated.
        """
        opts = cls._meta
        opts._prepare(cls)

        if opts.order_with_respect_to:
            cls.get_next_in_order = curry(cls._get_next_or_previous_in_order,
                                          is_next=True)
            cls.get_previous_in_order = curry(cls._get_next_or_previous_in_order,
                                              is_next=False)
            setattr(opts.order_with_respect_to.rel.to, 'get_%s_order' \
                    % cls.__name__.lower(), curry(method_get_order, cls))
            setattr(opts.order_with_respect_to.rel.to, 'set_%s_order' \
                    % cls.__name__.lower(), curry(method_set_order, cls))

        # Give the class a docstring -- its definition.
        if cls.__doc__ is None:
            cls.__doc__ = "%s(%s)" % (cls.__name__,
                                      ", ".join([f.attname for f in opts.fields]))

        if hasattr(cls, 'get_absolute_url'):
            cls.get_absolute_url = update_wrapper(curry(get_absolute_url,
                                                        opts, cls.get_absolute_url),
                                                  cls.get_absolute_url)

        if hasattr(cls, 'get_resource_url_list'):
            cls.get_resource_url_list = staticmethod(curry(get_resource_url_list,
                                                           opts, cls.get_resource_url_list))

        if hasattr(cls, 'get_resource_url_count'):
            cls.get_resource_url_count = curry(get_resource_url_count, opts,
                                               cls.get_resource_url_count)

        if hasattr(cls, 'get_resource_url_detail'):
            cls.get_resource_url_detail = curry(get_resource_url_detail, opts,
                                                cls.get_resource_url_detail)

        signals.class_prepared.send(sender=cls)


class ROAModel(models.Model):
    """
    Model which access remote resources.
    """
    __metaclass__ = ROAModelBase

    @staticmethod
    def get_resource_url_list():
        raise Exception, "Static method get_resource_url_list is not defined."

    def get_resource_url_count(self):
        return u"%scount/" % (self.get_resource_url_list(),)

    def get_resource_url_detail(self):
        return u"%s%s/" % (self.get_resource_url_list(), self.pk)

    def save_base(self, raw=False, cls=None, origin=None, force_insert=False,
            force_update=False, using=None):
        """
        Does the heavy-lifting involved in saving. Subclasses shouldn't need to
        override this method. It's separate from save() in order to hide the
        need for overrides of save() to pass around internal-only parameters
        ('raw', 'cls', and 'origin').
        """
        assert not (force_insert and force_update)
        if cls is None:
            cls = self.__class__
            meta = cls._meta
            if not meta.proxy:
                origin = cls
        else:
            meta = cls._meta

        if origin and not getattr(meta, "auto_created", False):
            signals.pre_save.send(sender=origin, instance=self, raw=raw)

        # If we are in a raw save, save the object exactly as presented.
        # That means that we don't try to be smart about saving attributes
        # that might have come from the parent class - we just save the
        # attributes we have been given to the class we have been given.
        # We also go through this process to defer the save of proxy objects
        # to their actual underlying model.
        if not raw or meta.proxy:
            if meta.proxy:
                org = cls
            else:
                org = None
            for parent, field in meta.parents.items():
                # At this point, parent's primary key field may be unknown
                # (for example, from administration form which doesn't fill
                # this field). If so, fill it.
                if field and getattr(self, parent._meta.pk.attname) is None \
                   and getattr(self, field.attname) is not None:
                    setattr(self, parent._meta.pk.attname, getattr(self, field.attname))

                self.save_base(cls=parent, origin=org)

                if field:
                    setattr(self, field.attname, self._get_pk_val(parent._meta))
            if meta.proxy:
                return

        if not meta.proxy:
            pk_val = self._get_pk_val(meta)
            pk_set = pk_val is not None

            get_args = {'format': ROA_FORMAT}
            get_args.update(getattr(settings, "ROA_CUSTOM_ARGS", {}))

            serializer = serializers.get_serializer(ROA_FORMAT)
            if hasattr(serializer, 'serialize_object'):
                payload = serializer().serialize_object(self)
            else:
                payload = {}
                for field in meta.local_fields:
                    # Handle FK fields
                    if isinstance(field, models.ForeignKey):
                        field_attr = getattr(self, field.name)
                        if field_attr is None:
                            payload[field.attname] = None
                        else:
                            payload[field.attname] = field_attr.pk
                    # Handle all other fields
                    else:
                        payload[field.name] = field.value_to_string(self)

                # Handle M2M relations in case of update
                if force_update or pk_set and not self.pk is None:
                    for field in meta.many_to_many:
                        # First try to get ids from var set in query's add/remove/clear
                        if hasattr(self, '%s_updated_ids' % field.attname):
                            field_pks = getattr(self, '%s_updated_ids' % field.attname)
                        else:
                            field_pks = [obj.pk for obj in field.value_from_object(self)]
                        payload[field.attname] = ','.join(smart_unicode(pk) for pk in field_pks)

            if force_update or pk_set and not self.pk is None:
                record_exists = True
                resource = Resource(self.get_resource_url_detail(),
                                    headers=ROA_HEADERS,
                                    filters=ROA_FILTERS)
                try:
                    logger.debug(u"""Modifying : "%s" through %s
                                  with payload "%s" and GET args "%s" """ % (
                                  force_unicode(self),
                                  force_unicode(resource.uri),
                                  force_unicode(payload),
                                  force_unicode(get_args)))
                    response = resource.put(payload=payload, **get_args)
                except RequestFailed, e:
                    raise ROAException(e)
            else:
                record_exists = False
                resource = Resource(self.get_resource_url_list(),
                                    headers=ROA_HEADERS,
                                    filters=ROA_FILTERS)
                try:
                    logger.debug(u"""Creating  : "%s" through %s
                                  with payload "%s" and GET args "%s" """ % (
                                  force_unicode(self),
                                  force_unicode(resource.uri),
                                  force_unicode(payload),
                                  force_unicode(get_args)))
                    response = resource.post(payload=payload, **get_args)
                except RequestFailed, e:
                    raise ROAException(e)

            response = force_unicode(response.body_string()).encode(DEFAULT_CHARSET)

            for local_name, remote_name in ROA_MODEL_NAME_MAPPING:
                response = response.replace(remote_name, local_name)

            deserializer = serializers.get_deserializer(ROA_FORMAT)
            if hasattr(deserializer, 'deserialize_object'):
                result = deserializer(response).deserialize_object(response)
            else:
                result = deserializer(response).next()

            try:
                self.pk = int(result.object.pk)
            except ValueError:
                self.pk = result.object.pk
            self = result.object

        if origin:
            signals.post_save.send(sender=origin, instance=self,
                created=(not record_exists), raw=raw)

    save_base.alters_data = True

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted " \
                "because its %s attribute is set to None." \
                % (self._meta.object_name, self._meta.pk.attname)

        # Deletion in cascade should be done server side.
        resource = Resource(self.get_resource_url_detail(),
                            headers=ROA_HEADERS,
                            filters=ROA_FILTERS)

        logger.debug(u"""Deleting  : "%s" through %s""" % \
            (unicode(self), unicode(resource.uri)))

        delete_args = getattr(settings, "ROA_CUSTOM_ARGS", {})
        resource.delete(**delete_args)

    delete.alters_data = True

    def _get_unique_checks(self, exclude=None):
        """
        We don't want to check unicity that way for now.
        """
        unique_checks, date_checks = [], []
        return unique_checks, date_checks


##############################################
# HELPER FUNCTIONS (CURRIED MODEL FUNCTIONS) #
##############################################

ROA_URL_OVERRIDES_LIST = getattr(settings, 'ROA_URL_OVERRIDES_LIST', {})
ROA_URL_OVERRIDES_COUNT = getattr(settings, 'ROA_URL_OVERRIDES_COUNT', {})
ROA_URL_OVERRIDES_DETAIL = getattr(settings, 'ROA_URL_OVERRIDES_DETAIL', {})

def get_resource_url_list(opts, func, *args, **kwargs):
    key = '%s.%s' % (opts.app_label, opts.module_name)
    overridden = ROA_URL_OVERRIDES_LIST.get(key, False)
    return overridden and overridden or func(*args, **kwargs)

def get_resource_url_count(opts, func, self, *args, **kwargs):
    key = '%s.%s' % (opts.app_label, opts.module_name)
    return ROA_URL_OVERRIDES_COUNT.get(key, func)(self, *args, **kwargs)

def get_resource_url_detail(opts, func, self, *args, **kwargs):
    key = '%s.%s' % (opts.app_label, opts.module_name)
    return ROA_URL_OVERRIDES_DETAIL.get(key, func)(self, *args, **kwargs)
