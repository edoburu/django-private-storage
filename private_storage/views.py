"""
Views to send private files.
"""
from django.http import HttpResponseForbidden, Http404
from django.views.generic import View

from . import appconfig
from .models import PrivateFile
from .servers import get_server_class
from .storage import private_storage
from .utils import import_symbol


class PrivateStorageView(View):
    """
    Return the uploaded files
    """

    #: The storage class to retrieve files from
    storage = private_storage

    #: The authorisation rule for accessing
    can_access_file = import_symbol(appconfig.PRIVATE_STORAGE_AUTH_FUNCTION)

    #: Import the server class once
    server_class = get_server_class(appconfig.PRIVATE_STORAGE_SERVER)

    def get(self, request, *args, **kwargs):
        """
        Handle incoming GET requests
        """
        # Wrap all relevant data in a single object,
        # so this is easy to extend and server implementations can pick what they need.
        private_file = PrivateFile(
            request=self.request,
            storage=self.storage,
            relative_name=self.kwargs['path']
        )

        if not self.can_access_file(private_file):
            return HttpResponseForbidden('Private storage access denied')

        if not private_file.exists():
            raise Http404("File not found")

        return self.serve_file(private_file)

    def serve_file(self, private_file):
        """
        Serve the file that was retrieved from the storage.
        The relative path can be found in ``self.kwargs['path']``.
        """
        return self.server_class().serve(private_file)
