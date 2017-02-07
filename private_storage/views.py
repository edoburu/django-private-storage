"""
Views to send private files.
"""
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
        return self.server_class().serve(private_file)


class PrivateStorageDetailView(SingleObjectMixin, PrivateStorageView):
    """
    Download a document based on an object ID.
    This view can by used by third-party apps to implement their own download view.

    Implement access controls by overriding :meth`get_queryset` or redefining :meth:`can_access_file`.
    """
    model = None  #
    model_file_field = 'file'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_path(self):
        file = getattr(self.object, 'file')
        return file.name

    def can_access_file(self, private_file):
        """
        The authorization rule for this view.
        By default it reuses the ``PRIVATE_STORAGE_AUTH_FUNCTION`` setting,
        but this should likely be redefined.
        """
        return PrivateStorageView.can_access_file(private_file)
