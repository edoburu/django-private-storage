.. image:: https://img.shields.io/travis/edoburu/django-private-storage/master.svg?branch=master
    :target: http://travis-ci.org/edoburu/django-private-storage
.. image:: https://img.shields.io/pypi/v/django-private-storage.svg
    :target: https://pypi.python.org/pypi/django-private-storage/
.. image:: https://img.shields.io/pypi/l/django-private-storage.svg
    :target: https://pypi.python.org/pypi/django-private-storage/
.. image:: https://img.shields.io/codecov/c/github/edoburu/django-private-storage/master.svg
    :target: https://codecov.io/github/edoburu/django-private-storage?branch=master

django-private-storage
======================

This module offers a private media file storage,
so user uploads can be protected behind a login.

It uses the Django storage API's internally,
so all form rendering and admin integration work out of the box.

Installation
============

::

    pip install django-private-storage

Configuration
-------------

Add to the settings:

.. code-block:: python

    INSTALLED_APPS += (
        'private_storage',
    )

    PRIVATE_STORAGE_ROOT = '/path/to/private-media/'
    PRIVATE_STORAGE_AUTH_FUNCTION = 'private_storage.permissions.allow_staff'

Add to ``urls.py``:

.. code-block:: python

    import private_storage.urls

    urlpatterns += [
        url('^private-media/', include(private_storage.urls)),
    ]

Usage
-----

In a Django model, add the ``PrivateFileField``:

.. code-block:: python

    from django.db import models
    from private_storage.fields import PrivateFileField

    class MyModel(models.Model):
        title = models.CharField("Title", max_length=200)
        file = PrivateFileField("File")

The ``PrivateFileField`` also accepts the following kwargs:

* ``upload_to``: the optional subfolder in the ``PRIVATE_STORAGE_ROOT``.
* ``upload_subfolder``: a function that defines the folder, it receives the current model ``instance``.
* ``content_types``: allowed content types
* ``max_file_size``: maximum file size in bytes. (1MB is 1024 * 1024)
* ``storage``: the storage object to use, defaults to ``private_storage.storage.private_storage``

Other topics
============

Storing files on Amazon S3
--------------------------

The ``PRIVATE_STORAGE_CLASS`` setting can be redefined to point to a different storage class.
The default is ``private_storage.storage.files.PrivateFileSystemStorage``, which uses
a private media folder that ``PRIVATE_STORAGE_ROOT`` points to.

Define one of these settings instead:

.. code-block:: python

    PRIVATE_STORAGE_CLASS = 'private_storage.storage.s3boto3.PrivateS3BotoStorage'

    AWS_PRIVATE_STORAGE_BUCKET_NAME = 'private-files'  # bucket name

This uses django-storages_ settings. Replace the prefix ``AWS_`` with ``AWS_PRIVATE_``.
The following settings are reused when they don't have an corresponding ``AWS_PRIVATE_...`` setting:

* ``AWS_ACCESS_KEY_ID``
* ``AWS_SECRET_ACCESS_KEY``
* ``AWS_S3_URL_PROTOCOL``
* ``AWS_S3_REGION_NAME``
* ``AWS_IS_GZIPPED``

All other settings should be explicitly defined with ``AWS_PRIVATE_...`` settings.

By default, all URLs in the admin return the direct S3 bucket URls, with the `query parameter authentication`_ enabled.
When ``AWS_PRIVATE_QUERYSTRING_AUTH = False``, all file downloads are proxied through our ``PrivateFileView`` URL.
This behavior can be enabled explicitly using ``PRIVATE_STORAGE_S3_REVERSE_PROXY = True``.

To have encryption either configure ``AWS_PRIVATE_S3_ENCRYPTION``
and ``AWS_PRIVATE_S3_SIGNATURE_VERSION`` or use:

.. code-block:: python

    PRIVATE_STORAGE_CLASS = 'private_storage.storage.s3boto3.PrivateEncryptedS3BotoStorage'

Make sure an encryption key is generated on Amazon.

Defining access rules
---------------------

The ``PRIVATE_STORAGE_AUTH_FUNCTION`` defines which user may access the files.
By default, this only includes superusers.

The following options are available out of the box:

* ``private_storage.permissions.allow_authenticated``
* ``private_storage.permissions.allow_staff``
* ``private_storage.permissions.allow_superuser``

You can create a custom function, and use that instead.
The function receives a ``private_storate.models.PrivateFile`` object,
which has the following fields:

* ``request``: the Django request.
* ``storage``: the storage engine used to retrieve the file.
* ``relative_name``: the file name in the storage.
* ``full_path``: the full file system path.
* ``exists()``: whether the file exists.
* ``content_type``: the HTTP content type.
* ``parent_object``: only set when ``PrivateStorageDetailView`` was used.


Retrieving files by object ID
-----------------------------

To implement more object-based access permissions,
create a custom view that provides the download.

.. code-block:: python

    from private_storage.views import PrivateStorageDetailView

    class MyDocumentDownloadView(PrivateStorageDetailView):
        model = MyModel
        model_file_field = 'file'

        def get_queryset(self):
            # Make sure only certain objects can be accessed.
            return super().get_queryset().filter(...)

        def can_access_file(self, private_file):
            # When the object can be accessed, the file may be downloaded.
            # This overrides PRIVATE_STORAGE_AUTH_FUNCTION
            return True

The following class-level attributes can be overwritten:

* ``model``: The model to fetch (including every other attribute of ``SingleObjectMixin``).
* ``model_file_field``: This should point to the field used to store the file.
* ``storage`` / ``get_storage()``: The storage class to read the file from.
* ``server_class``: The Python class used to generate the ``HttpResponse`` / ``FileResponse``.
* ``content_disposition``: Can be "inline" (show inside the browser) or "attachment" (saved as download).
* ``content_disposition_filename`` / ``get_content_disposition_filename()``: Overrides the filename for downloading.


Optimizing large file transfers
-------------------------------

Sending large files can be inefficient in some configurations.

In the worst case scenario, the whole file needs to be read in chunks
and passed as a whole through the WSGI buffers, OS kernel, webserver and proxy server.
In effect, the complete file is copied several times through memory buffers.

There are more efficient ways to transfer files, such as the ``sendfile()`` system call on UNIX.
Django uses such feature when the WSGI server provides ``wsgi.file_handler`` support.

In some situations, this effect is nullified,
for example by by a local HTTP server sitting in front of the WSGI container.
A typical case would be  running Gunicorn behind an Nginx or Apache webserver.

For such situation, the native support of the
webserver can be enabled with the following settings:

For apache
~~~~~~~~~~

.. code-block:: python

    PRIVATE_STORAGE_SERVER = 'apache'

For Nginx
~~~~~~~~~

.. code-block:: python

    PRIVATE_STORAGE_SERVER = 'nginx'
    PRIVATE_STORAGE_INTERNAL_URL = '/private-x-accel-redirect/'

Add the following location block in the server config:

.. code-block:: nginx

    location /private-x-accel-redirect/ {
      internal;
      alias   /path/to/private-media/;
    }

For very old Nginx versions, you'll have to configure ``PRIVATE_STORAGE_NGINX_VERSION``,
because Nginx versions before 1.5.9 (released in 2014) handle non-ASCII filenames differently.

Other webservers
~~~~~~~~~~~~~~~~

The ``PRIVATE_STORAGE_SERVER`` may also point to a dotted Python class path.
Implement a class with a static ``serve(private_file)`` method.

Using multiple storages
-----------------------

The ``PrivateFileField`` accepts a ``storage`` kwarg,
hence you can initialize multiple ``private_storage.storage.PrivateStorage`` objects,
each providing files from a different ``location`` and ``base_url``.

For example:

.. code-block:: python


    from django.db import models
    from private_storage.fields import PrivateFileField
    from private_storage.storage.files import PrivateFileSystemStorage

    my_storage = PrivateFileSystemStorage(
        location='/path/to/storage2/',
        base_url='/private-documents2/'
    )

    class MyModel(models.Model):
        file = PrivateFileField(storage=my_storage)


Then create a view to serve those files:

.. code-block:: python

    from private_storage.views import PrivateStorageView
    from .models import my_storage

    class MyStorageView(PrivateStorageView):
        storage = my_storage

        def can_access_file(self, private_file):
            # This overrides PRIVATE_STORAGE_AUTH_FUNCTION
            return self.request.is_superuser

And expose that URL:

.. code-block:: python

    urlpatterns += [
        url('^private-documents2/(?P<path>.*)$', views.MyStorageView.as_view()),
    ]


Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!


.. _django-storages: https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
.. _query parameter authentication: https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-query-string-auth.html
