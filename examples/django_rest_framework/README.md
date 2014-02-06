How to run tests:
================

Launch two terminals

Backend part
------------

In first terminal:

    $ cd examples/django_rest_framework/backend/
    $ bash load.sh

Frontend part
-------------

In second terminal:

    $ examples/django_rest_framework/frontend/
    $ python manage.py test frontend

After each test command, please re-run backend load command.


