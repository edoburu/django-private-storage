"""
Sending files efficiently for different kind of webservers.
"""
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import FileResponse, HttpResponse
from django.http import HttpResponseNotModified
from django.utils.http import http_date
from django.utils.lru_cache import lru_cache
from django.utils.module_loading import import_string
from django.views.static import serve, was_modified_since


@lru_cache()
def get_server_class(path):
    if '.' in path:
        return import_string(path)
    elif path == 'streaming':
        return DjangoStreamingServer
    elif path == 'django':
        return DjangoServer
    elif path == 'apache':
        return ApacheXSendfileServer
    elif path == 'nginx':
        return NginxXAccelRedirectServer
    else:
        raise ImproperlyConfigured(
            "PRIVATE_STORAGE_SERVER setting should be 'nginx', 'apache', 'django' or a python class path."
        )


class DjangoStreamingServer(object):
    """
    Serve static files as streaming chunks in Django.
    """

    @staticmethod
    def serve(private_file):
        # Support If-Last-Modified
        mtime = private_file.modified_time.timestamp()
        size = private_file.size
        if not was_modified_since(private_file.request.META.get('HTTP_IF_MODIFIED_SINCE'), mtime, size):
            return HttpResponseNotModified()

        # FileResponse will submit the file in 8KB chunks
        response = FileResponse(private_file.open())
        response['Content-Type'] = private_file.content_type
        response['Content-Length'] = size
        response["Last-Modified"] = http_date(mtime)
        return response


class DjangoServer(DjangoStreamingServer):
    """
    Serve static files from the local filesystem through Django.
    This is a bad idea for most situations other than testing.
    The file data is copied multiple times; read by Django, written to WSGI,
    read by webserver, outputted to client.
    """

    @staticmethod
    def serve(private_file):
        # This supports If-Modified-Since and sends the file in 8KB chunks
        try:
            full_path = private_file.full_path
        except NotImplementedError:
            # S3 files, fall back to streaming server
            return DjangoStreamingServer.serve(private_file)
        else:
            # Using Django's serve gives If-Modified-Since support out of the box.
            return serve(private_file.request, full_path, document_root='/', show_indexes=False)


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
