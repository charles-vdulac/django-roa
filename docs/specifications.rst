=========================
Django ROA specifications
=========================

Client
======

Model
-----

Available methods and limitations:

    * save(): Creates or updates the object
    * delete(): Deletes the object, do not delete in cascade


Manager
-------

Available methods and limitations:

    * all(): Returns all the elements of a QuerySet
    * get_or_create(): Get or create an object
    * delete(): Deletes the records in the current QuerySet
    * filter(): Returns a filtered QuerySet, do not handle Q objects
    * exclude(): Returns a filtered QuerySet, do not handle Q objects
    * order_by(): Returns an ordered QuerySet
    * count(): Returns the number of elements of a QuerySet
    * latest(): Returns the latest element of a QuerySet
    * [start:end]: Returns a sliced QuerySet, useful for pagination


Server
======

URLs
----

Required URLs and limitations:

    * /{resource}/: used for retrieving lists (GET) or creating objects (POST)
    * /{resource}/{id}/: used for retrieving an object (GET), updating it 
      (PUT) or deleting (DELETE) it

Note: URL id is required but you can choose a totally different URL scheme
given the ``resource_url_detail`` property.


Parameters
----------

Optionnal parameters:

    * format: json, xml will be supported as soon as possible
    * count: returns the number of elements
    * filter_* and exclude_*: * is the string used by Django to filter/exclude
    * order_by: order the results given this field
    * limit_start and limit_stop: slice the results given those integers

Note: take a look at tests and test_projects to see all actual possibilities.
