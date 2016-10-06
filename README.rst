django-private-storage
======================

This module offers a private media file storage,
so user uploads can be protected behind a login.

Installation
============

::

    pip install django-private-storage

Configuration
-------------

Add to ``urls.py``:

.. code-block:: python

    import private_storage.urls

    urlpatterns += [
        url('^private-media/', include(private_storage.urls)),
    ]

Add to the settings:

.. code-block:: python

    PRIVATE_STORAGE_ROOT = '/path/to/private-media/'
    PRIVATE_STORAGE_AUTH_FUNCTION = 'apps.utils.private_storage.permissions.allow_staff'

Usage
-----

In a Django model, add the ``PrivateFileField``:

.. code-block:: python

    from django.db import models
    from private_storage.fields import PrivateFileField

    class MyModel(models.Model):
        title = models.CharField("Title", max_length=200)
        file = PrivateFileField("Title")

The ``PrivateFileField`` also accepts the following kwargs:

* ``upload_to``: the subfolder in the ``PRIVATE_STORAGE_ROOT``.
* ``upload_subfolder``: a function that defines the folder, it receives the current model ``instance``.
* ``content_types``: allowed content types
* ``max_file_size``: maximum file size.

Other topics
============

Defining access rules
---------------------

The ``PRIVATE_STORAGE_AUTH_FUNCTION`` defines which user may access the files.
By default, this only includes superusers.

The function receives a ``private_storate.models.PrivateFile`` object,
which has the following fields:

* ``request``: the Django request.
* ``storage``: the storage engine used to retrieve the file.
* ``relative_name``: the file name in the storage.
* ``full_path``: the full file system path.
* ``exists()``: whether the file exists.
* ``content_type``: the HTTP content type.

Optimizing large file transfers
-------------------------------

By default, the files are served by the Django instance.
This can be inefficient, since the whole file needs to be read in chunks
and passed through the WSGI buffers, OS kernel and webserver.
In effect, the complete file is copied several times through memory buffers.

Hence, webservers offer a method to send the file on behalf of the backend application.
This happens with the ``sendfile()`` system call,
which can be enabled with the following settings:

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

Other webservers
~~~~~~~~~~~~~~~~

The ``PRIVATE_STORAGE_SERVER`` may also point to a dotted Python class path.
Implement a class with a static ``serve(private_file)`` method.

Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!
