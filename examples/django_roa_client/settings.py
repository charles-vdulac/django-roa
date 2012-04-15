import os
ROOT_PATH = os.path.dirname(__file__)

TEMPLATE_DEBUG = DEBUG = True
MANAGERS = ADMINS = ()
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(ROOT_PATH, 'testdb.sqlite')

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = '2+@4vnr#v8e273^+a)g$8%dre^dwcn#d&n#8+l6jk7r#$p&3zk'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
ROOT_URLCONF = 'urls'
TEMPLATE_DIRS = (os.path.join(ROOT_PATH, '../../templates'),)
INSTALLED_APPS = (
    'django_roa',
    'django_roa.remoteauth',
    'django_roa_client',
    #'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
)
AUTHENTICATION_BACKENDS = (
    'django_roa.remoteauth.backends.RemoteUserModelBackend',
)
SESSION_ENGINE = "django.contrib.sessions.backends.file"
SERIALIZATION_MODULES = {
    'django' : 'examples.django_roa_client.serializers',
}

## ROA custom settings
ROA_MODELS = True # set to False if you'd like to develop/test locally
ROA_FORMAT = 'django' # json or xml
# specify the headers sent to the ws from restkit
ROA_HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
}
ROA_DJANGO_ERRORS = True # useful to ease debugging if you use test server

ROA_URL_OVERRIDES_LIST = {
    'django_roa_client.remotepagewithoverriddenurls': u'http://127.0.0.1:8081/django_roa_server/remotepagewithoverriddenurls/',
}
ROA_URL_OVERRIDES_DETAIL = {
    'django_roa_client.remotepagewithoverriddenurls': lambda o: u"%s%s-%s/" % (o.get_resource_url_list(), o.id, o.slug),
}
ROA_MODEL_NAME_MAPPING = (
    # local name: remote name
    ('django_roa_client.', 'django_roa_server.'),
    ('remoteauth.', 'auth.'),
)
ROA_ARGS_NAMES_MAPPING = {
    'ORDER_BY': 'order',
}
# Enable HTTP authentication through django-piston
from restkit import BasicAuth
ROA_FILTERS = [ BasicAuth('django-roa', 'roa'), ]
# Disable authentication through django-piston
#ROA_FILTERS = []

## Logging settings
import logging
logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(message)s")
