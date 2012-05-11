#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = 'django-roa',
    version = '1.7',
    url = 'http://code.welldev.org/django-roa/wiki/Home',
	download_url = 'http://code.welldev.org/django-roa/downloads/',
    license = 'BSD',
    description = "Turn your models into remote resources that you can access through Django's ORM.",
    author = 'David Larlet',
    author_email = 'david@larlet.fr',
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
