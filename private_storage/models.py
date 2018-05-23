import mimetypes

from django.core.files.storage import File, Storage
from django.utils.functional import cached_property


class PrivateFile(object):
    """
    A wrapper object that describes the file that is being accessed.
    """

    def __init__(self, request, storage, relative_name, parent_object=None):
        self.request = request
        self.storage = storage  # type: Storage
        self.relative_name = relative_name
        self.parent_object = parent_object

    def __repr__(self):
        return '<PrivateFile: {}>'.format(self.relative_name)

    @cached_property
    def full_path(self):
        # Not using self.storage.open() as the X-Sendfile needs a normal path.
        return self.storage.path(self.relative_name)

    def open(self, mode='rb'):
        """
        Open the file for reading.
        :rtype: django.core.files.storage.File
        """
        file = self.storage.open(self.relative_name, mode=mode)  # type: File
        return file

    def exists(self):
        """
        Check whether the file exists.
        """
        return self.relative_name and self.storage.exists(self.relative_name)

    @cached_property
    def content_type(self):
        """
        Return the HTTP ``Content-Type`` header value for a filename.
        """
        mimetype, encoding = mimetypes.guess_type(self.relative_name)
        return mimetype or 'application/octet-stream'

    @cached_property
    def size(self):
        """
        Return the size of the file in bytes.
        """
        return self.storage.size(self.relative_name)

    @cached_property
    def modified_time(self):
        """
        Return the last-modified time
        """
        return self.storage.get_modified_time(self.relative_name)
