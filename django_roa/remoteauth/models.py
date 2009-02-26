import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission as DjangoPermission, User, \
    Group as DjangoGroup, get_hexdigest, check_password, UserManager, Message
from django.utils.translation import ugettext_lazy as _
from django.db import models

from django_roa import Model, Manager

class RemotePermission(Model, DjangoPermission):
    """
    Inherits methods from Django's Permission model.
    """
    name = models.CharField(_('name'), max_length=50)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField(_('codename'), max_length=100)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/auth/permission/'


class RemoteGroup(Model, DjangoGroup):
    """
    Inherits methods from Django's Group model.
    """
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(RemotePermission, verbose_name=_('permissions'), blank=True)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/auth/group/'


class RemoteUserManager(Manager, UserManager):
    """
    Inherits methods from Django's UserManager manager.
    """

class RemoteUser(Model, User):
    """
    Inherits methods from Django's User model.
    """
    username = models.CharField(max_length=30)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('e-mail address'), blank=True)
    password = models.CharField(_('password'), max_length=128, help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_("Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(_('active'), default=True, help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."))
    is_superuser = models.BooleanField(_('superuser status'), default=False, help_text=_("Designates that this user has all permissions without explicitly assigning them."))
    last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    date_joined = models.DateTimeField(_('date joined'), default=datetime.datetime.now)
    groups = models.ManyToManyField(RemoteGroup, verbose_name=_('groups'), blank=True,
        help_text=_("In addition to the permissions manually assigned, this user will also get all permissions granted to each group he/she is in."))
    user_permissions = models.ManyToManyField(RemotePermission, verbose_name=_('user permissions'), blank=True)
    objects = RemoteUserManager()

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/auth/user/'


class Message(Model, Message):
    """
    Inherits methods from Django's Message model.
    """
    user = models.ForeignKey(RemoteUser)
    message = models.TextField(_('message'))

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/auth/message/'
