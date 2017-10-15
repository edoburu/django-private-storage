"""
Views to send private files.
"""
import os

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote  # Python 2

from django.http import HttpResponseForbidden, Http404
from django.utils.module_loading import import_string
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from . import appconfig
from .models import PrivateFile
from .servers import get_server_class
from .storage import private_storage


class PrivateStorageView(View):
    """
    Return the uploaded files
    """

    #: The storage class to retrieve files from
    storage = private_storage

    #: The authorisation rule for accessing
    can_access_file = staticmethod(import_string(appconfig.PRIVATE_STORAGE_AUTH_FUNCTION))

    #: Import the server class once
    server_class = get_server_class(appconfig.PRIVATE_STORAGE_SERVER)

    #: Whether the file should be displayed ``inline`` or show a download box (``attachment``).
    content_disposition = None

    #: The filename to use when :attr:`content_disposition` is set.
    content_disposition_filename = None

    def get_path(self):
        """
        Determine the path for the object to provide.
        This can be overwritten to combine the view with a different object retrieval.
        """
        return self.kwargs['path']

    def get_private_file(self):
        """
        Return all relevant data in a single object, so this is easy to extend
        and server implementations can pick what they need.
        """
        return PrivateFile(
            request=self.request,
            storage=self.storage,
            relative_name=self.get_path()
        )

    def get(self, request, *args, **kwargs):
        """
        Handle incoming GET requests
        """
        private_file = self.get_private_file()

        if not self.can_access_file(private_file):
            return HttpResponseForbidden('Private storage access denied')

        if not private_file.exists():
            raise Http404("File not found")

        return self.serve_file(private_file)

    def serve_file(self, private_file):
        """
        Serve the file that was retrieved from the storage.
        The relative path can be found with ``private_file.relative_name``.

        :type private_file: :class:`private_storage.models.PrivateFile`
        :rtype: django.http.HttpResponse
        """
        response = self.server_class().serve(private_file)

        if self.content_disposition:
            filename = self.get_content_disposition_filename(private_file)
            response['Content-Disposition'] = '{}; {}'.format(
                self.content_disposition, self._encode_filename_header(filename)
            )

        return response

    def get_content_disposition_filename(self, private_file):
        """
        Return the filename in the download header.
        """
        return self.content_disposition_filename or os.path.basename(private_file.relative_name)

    def _encode_filename_header(self, filename):
        """
        The filename, encoded to use in a ``Content-Disposition`` header.
        """
        # Based on https://www.djangosnippets.org/snippets/1710/
        if 'WebKit' in self.request.META['HTTP_USER_AGENT']:
            # Support available for UTF-8 encoded strings.
            utf8_filename = filename.encode("utf-8")
            return 'filename={}'.format(utf8_filename)
        elif 'MSIE' in self.request.META['HTTP_USER_AGENT']:
            # IE does not support internationalized filename at all.
            # It can only recognize internationalized URL, so we should perform a trick via URL names.
            return ''
        else:
            # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
            rfc2231_filename = quote(filename.encode("utf-8"))
            return "filename*=UTF-8''{}".format(rfc2231_filename)


class PrivateStorageDetailView(SingleObjectMixin, PrivateStorageView):
    """
    Download a document based on an object ID.
    This view can by used by third-party apps to implement their own download view.

    Implement access controls by overriding :meth`get_queryset` or redefining :meth:`can_access_file`.
    """

    #: Define the model to fetch.
    model = None

    #: Define which field the file name is stored at.
    model_file_field = 'file'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(PrivateStorageDetailView, self).get(request, *args, **kwargs)

    def get_path(self):
        file = getattr(self.object, self.model_file_field)
        return file.name

    def get_private_file(self):
        # Provide the parent object as well.
        return PrivateFile(
            request=self.request,
            storage=self.storage,
            relative_name=self.get_path(),
            parent_object=self.object
        )

    def can_access_file(self, private_file):
        """
        The authorization rule for this view.
        By default it reuses the ``PRIVATE_STORAGE_AUTH_FUNCTION`` setting,
        but this should likely be redefined.
        """
        return PrivateStorageView.can_access_file(private_file)
