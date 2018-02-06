Changelog
=========

Changes in git
--------------

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
