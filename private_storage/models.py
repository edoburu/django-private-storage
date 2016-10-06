import mimetypes
import os

from django.utils.functional import cached_property


class PrivateFile(object):
    """
    A wrapper object that describes the file that is being accessed.
    """

    def __init__(self, request, storage, relative_name):
        self.request = request
        self.storage = storage
        self.relative_name = relative_name

    @cached_property
    def full_path(self):
        # Not using self.storage.open() as the X-Sendfile needs a normal path.
        return self.storage.path(self.relative_name)

    def exists(self):
        return os.path.exists(self.full_path)

    @cached_property
    def content_type(self):
        """
        Return the HTTP ``Content-Type`` header value for a filename.
        """
        mimetype, encoding = mimetypes.guess_type(self.full_path)
        return mimetype or 'application/octet-stream'
