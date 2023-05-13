Changelog
=========

Changes in 3.1 (2023-05-12)
---------------------------

* Fixed compatibility for Django 4.1, 4.2


Version 3.0 (2021-11-16)
------------------------

* Added Django 4 support.
* Added minio storage support.


Changes in 2.3 (2021-05-17)
---------------------------

* Added PrivateImageField.
* Added French locale.
* Fixed support for django-storages > 1.10.
* Fixed Django 4 deprecation warnings
* Dropped Python 2.7/3.4/3.5 support.
* Dropped Django 1.8/1.9/1.10/1.11 support.


Changes in 2.2.2 (2020-01-14)
-----------------------------

* Fixed Django 3.0 compatibility.


Changes in 2.2.1 (2019-11-04)
-----------------------------

* Make sure custom ``403.html`` template is used when access is denied.
* Fixed accessing files when the ``User-Agent`` header is not set.


Changes in 2.2 (2019-04-08)
---------------------------

* Added efficient ``HEAD`` request handling. (Already in 2.2a1 at 2018-11-22)


Changes in 2.1.3 (2018-09-10)
-----------------------------

* Fixed spelling error in "file too large" error.
* Fixed compatibility with latest django-storages_ which removed the ``strict`` setting keyword.


Changes in 2.1.2 (2018-05-23)
-----------------------------

* Fixed ``PrivateFile.exists()`` check for ``<FieldFile: None>`` values.
* Added ``PrivateFile.__repr__()``


Changes in 2.1.1 (2018-05-16)
-----------------------------

* Fixed ``X-Accel-Redirect`` non-ASCII filename encoding in Nginx.

 * For very old Nginx versions, you'll have to configure ``PRIVATE_STORAGE_NGINX_VERSION``,
   because Nginx versions before 1.5.9 (released in 2014) handle non-ASCII filenames differently.


Changes in 2.1 (2018-05-08)
---------------------------

* Added ``serve_file_not_found()`` to allow custom 404 serving in ``PrivateStorageView`` and ``PrivateStorageDetailView``.
* Added ``Cache-Control`` headers to avoid caching private files in edge proxies.
* Fixed ``PrivateStorageDetailView`` to use using the custom storage class defined in the model's ``PrivateFileField``.
* Fixed ``Content-Disposition`` filename encoding in Python 3.
* Fixed ``Content-Disposition`` filename support for old Internet Explorer browsers.


Changes in 2.0 (2018-02-06)
---------------------------

* Added Django 2.0 support.
* Support ``upload_to`` parameter and callable.
* Support ``upload_subfolder`` to return a string instead of list.
* Dropped Django 1.7 compatibility


Version 1.2.4 (2018-01-31)
--------------------------

* Fixed Python 2 support in ``DjangoStreamingServer.serve()``.


Version 1.2.3 (2017-12-04)
--------------------------

* Fixed ``reverse()`` import for Django 2.0.
* Fixed ``UnicodeDecodeError`` with cyrillic file names.
* Fixed Python 2 ``super()`` call.


Version 1.2.2 (2017-10-01)
--------------------------

* Fixed default ``PRIVATE_STORAGE_AUTH_FUNCTION`` path.
* Added ``PrivateFile.parent_object`` field when ``PrivateStorageDetailView`` is used.


Version 1.2.1 (2017-05-08)
--------------------------

* Fixed ``s3boto3`` backend on Django 1.8.


Version 1.2 (2017-04-05)
------------------------

* Added ``Content-Disposition`` header support, including a proper RFC-encoded filename.
  Add the ``content_disposition`` field to the views to enable this.
  The ``content_disposition_filename`` and ``get_content_disposition_filename()`` can be overwritten too.


Version 1.1.2 (2017-04-05)
--------------------------

* Allow AWS_PRIVATE.. credentials to be defined through environment variables too.
* Fixed ``model_file_field`` usage in ``PrivateStorageDetailView``.


Version 1.1.1 (2017-02-17)
--------------------------

* Implement proxying S3 content when ``AWS_PRIVATE_QUERYSTRING_AUTH`` is disabled.
  This can also be explicitly enabled using ``PRIVATE_STORAGE_S3_REVERSE_PROXY = True``.

Version 1.1 (2017-02-07)
------------------------

* Allow to configure the storage class, using ``PRIVATE_STORAGE_CLASS``.
  There are 3 storage classes available:

 * ``private_storage.storage.files.PrivateFileSystemStorage`` - the original, default.
 * ``private_storage.storage.s3boto3.PrivateS3BotoStorage`` - S3 bucket, based on django-storages_.
 * ``private_storage.storage.s3boto3.PrivateEncryptedS3BotoStorage`` - S3 bucket with encryption.

* Added ``PrivateStorageView.get_path()`` method for easier reuse.
* Added ``PrivateStorageDetailView`` for easier reuse in projects.
* Added ``@deconstructible`` for storage classes.
* Added ``private_storage.servers.DjangoStreamingServer`` to support streaming data from non-filesystem storages.
* Dropped Django 1.6 support.


Version 1.0.2 (2017-01-11)
--------------------------

* Fixed Python 3 issue with lazy URL resolving.
* Fixed ``TypeError`` when calling the access check function.
* Fixed file serving with ``PRIVATE_STORAGE_SERVER`` set to ``django``.


Version 1.0.1 (2016-10-10)
--------------------------

* Fixed packaging NL translation
* Fixed error message for too large files.


Version 1.0 (2016-10-10)
------------------------

First PyPI release.

The module design has been stable for quite some time,
so it's time to show this module to the public.


.. _django-storages: https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
