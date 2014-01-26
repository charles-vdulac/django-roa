import re
from django.utils import timezone
from django.core import validators
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission as DjangoPermission, \
    User as DjangoUser, Group as DjangoGroup, \
    UserManager as DjangoUserManager
try:
    from django.contrib.auth.models import Message as DjangoMessage
except ImportError:
    DjangoMessage = None
from django.utils.translation import ugettext_lazy as _
from django.db import models

from django_roa import Model, Manager


class Permission(Model, DjangoPermission):
    """
    Inherits methods from Django's Permission model.
    """
    name = models.CharField(_('name'), max_length=50)
    # non-standard related_name added to avoid clashes
    content_type = models.ForeignKey(ContentType, related_name="permissions")
    codename = models.CharField(_('codename'), max_length=100)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/auth/permission/'

    @classmethod
    def serializer(cls):
        from .serializers import PermissionSerializer
        return PermissionSerializer


class Group(Model, DjangoGroup):
    """
    Inherits methods from Django's Group model.
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission,
        verbose_name=_('permissions'), blank=True)

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/auth/group/'

    @classmethod
    def serializer(cls):
        from .serializers import GroupSerializer
        return GroupSerializer


class UserManager(Manager, DjangoUserManager):
    """
    Inherits methods from Django's UserManager manager.
    """


class User(Model, DjangoUser):
    """
    Inherits methods from Django's User model.
    """
    id = models.IntegerField(primary_key=True)
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    password = models.CharField(_('password'), max_length=128)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    is_superuser = models.BooleanField(_('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))
    groups = models.ManyToManyField(Group, verbose_name=_('groups'),
        blank=True, help_text=_('The groups this user belongs to. A user will '
                                'get all permissions granted to each of '
                                'his/her group.'),
        related_name="user_set", related_query_name="user")
    user_permissions = models.ManyToManyField(Permission,
        verbose_name=_('user permissions'), blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set", related_query_name="user")

    objects = UserManager()

    @staticmethod
    def get_resource_url_list():
        return u'http://127.0.0.1:8081/auth/user/'

    @classmethod
    def serializer(cls):
        from .serializers import UserSerializer
        return UserSerializer


Message = None

if DjangoMessage:
    class Message(Model, DjangoMessage):
        """
        Inherits methods from Django's Message model.
        """
        user = models.ForeignKey(User)
        message = models.TextField(_('message'))

        @staticmethod
        def get_resource_url_list():
            return u'http://127.0.0.1:8081/auth/message/'
