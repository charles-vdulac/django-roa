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
TEMPLATE_DIRS = (os.path.join(ROOT_PATH, 'templates'),)
INSTALLED_APPS = (
    'django_roa',
    'django_roa_server',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    #'django.contrib.admin',
)
SERIALIZATION_MODULES = {
    'custom' : 'examples.django_roa_client.serializers',
}
PISTON_DISPLAY_ERRORS = False

## Logging settings
import logging
logging.basicConfig(level=logging.DEBUG, format="%(name)s - %(message)s")
