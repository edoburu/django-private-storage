"""
Sending files efficiently for different kind of webservers.
"""
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.utils.lru_cache import lru_cache
from django.views.static import serve

from .utils import import_symbol


@lru_cache()
def get_server_class(path):
    if '.' in path:
        return import_symbol(path)
    elif path == 'django':
        return DjangoServer()
    elif path == 'apache':
        return ApacheXSendfileServer
    elif path == 'nginx':
        return NginxXAccelRedirectServer
    else:
        raise ImproperlyConfigured(
            "PRIVATE_STORAGE_SERVER setting should be 'nginx', 'apache', 'django' or a python class path."
        )


class DjangoServer(object):
    """
    Serve static files from the local filesystem through Django.
    This is a bad idea for most situations other than testing.
    The file data is copied multiple times; read by Django, written to WSGI,
    read by webserver, outputted to client.
    """

    @staticmethod
    def serve(private_file):
        # This supports If-Modified-Since and sends the file in 8KB chunks
        return serve(private_file.request, private_file.full_path, document_root='/', show_indexes=False)


class ApacheXSendfileServer(object):
    """
    Serve files for Apache with ``X-Sendfile``.
    """

    @staticmethod
    def serve(private_file):
        response = HttpResponse()
        response['X-Sendfile'] = private_file.full_path
        response['Content-Type'] = private_file.content_type
        return response


class NginxXAccelRedirectServer(object):
    """
    Serve the files for Nginx with ``X-Accel-Redirect``.
    Add the following configuration::

        location /private-x-accel-redirect/ (
            internal;
            alias /home/user/my/path/to/private/media/;
        )

    Or update the ``PRIVATE_STORAGE_INTERNAL_URL`` setting to use a different URL prefix.
    """

    @staticmethod
    def serve(private_file):
        internal_url = os.path.join(settings.PRIVATE_STORAGE_INTERNAL_URL, private_file.relative_name)
        response = HttpResponse()
        response['X-Accel-Redirect'] = internal_url
        response['Content-Type'] = private_file.content_type
        return response
