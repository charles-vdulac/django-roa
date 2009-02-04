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


Fields
------

Available fields:

    * Auto      # Custom AutoField doesn't work yet but default id one works
    * Boolean   # None doesn't work with json serialization, bug #5563 of Django
    * Char
    * Date
    * DateTime
    * Decimal
    * Email
    * FilePath
    * Float
    * Integer
    * Slug
    * Text
    * Time
    * URL


Relations
---------

Available relations:

    * ForeignKey
    * ManyToMany   # Patch from bug #10109 of Django required


Admin
-----

Available options: all except ``search_fields`` because of advanced querysets.


Server
======

URLs
----

Required URLs and limitations:

    * /{resource}/: used for retrieving lists (GET) or creating objects (POST)
    * /{resource}/{id}/: used for retrieving an object (GET), updating it 
      (PUT) or deleting (DELETE) it

Note: URL id is required but you can choose a totally different URL scheme
given the ``get_resource_url_*`` methods, a complete example is available in 
tests' projects.


Parameters
----------

Optional parameters:

    * count: returns the number of elements
    * filter_* and exclude_*: * is the string used by Django to filter/exclude
    * order_by: order the results given this field
    * limit_start and limit_stop: slice the results given those integers
    * format: json or xml

Optional M2M parameters:

    * m2m_add: declare that you will add many-to-many relations
    * m2m_remove: declare that you will remove many-to-many relations
    * m2m_clear: declare that you will clear many-to-many relations
    * m2m_field_name: name of the related field, required for add, remove and
      clear types of relations
    * m2m_ids: ids of the related objects, required for add and remove types
      of relations

Note: take a look at tests and examples to see all actual possibilities.


Settings
========

List of custom settings:

    * ``ROA_MODELS``: A boolean, turn to True if you'd like to access distant
      resources, useful to switch from a local development to a production 
      remote server in a breath.
    * ``ROA_FORMAT``: A string, turn to "xml" if you prefer this serialization 
      format over the default one (json). Note that json serialization doesn't
      work with BooleanFields set to None because of #5563 Django's bug.
    * ``ROA_DJANGO_ERRORS``: A boolean, turn to True if you use the 
      ``MethodDispatcher`` class from ``django_roa_server``, it will display 
      more readable errors.
    * ``ROA_URL_OVERRIDES_*``: A dictionary mapping "app_label.model_name" 
      strings to functions that take a model object and return its URL. This 
      is a way of overriding ``get_resource_url_*`` methods on a 
      per-installation basis. Note that the model name used in this setting 
      should be all lower-case, regardless of the case of the actual model 
      class name. Same behaviour as ``ABSOLUTE_URL_OVERRIDES`` setting, see
      examples.
