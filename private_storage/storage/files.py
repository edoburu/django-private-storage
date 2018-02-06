"""
Django Storage interface, using the file system backend.
"""
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text

from private_storage import appconfig

try:
    from django.urls import reverse_lazy  # Added in Django 1.10
except ImportError:
    from django.core.urlresolvers import reverse_lazy


@deconstructible
class PrivateFileSystemStorage(FileSystemStorage):
    """
    Interface to the Django storage system,
    storing the files in a private folder.
    """

    def __init__(self, location=None, base_url=None, **kwargs):
        if location is None:
            location = appconfig.PRIVATE_STORAGE_ROOT

        super(PrivateFileSystemStorage, self).__init__(
            location=location,
            base_url=base_url,
            **kwargs
        )
        if base_url is None:
            # When base_url is not given, it's autodetected.
            # However, as the super method checks for base_url.endswith('/'),
            # the attribute is overwritten here to avoid breaking lazy evaluation.
            self.base_url = reverse_lazy('serve_private_file', kwargs={'path': ''})

    def url(self, name):
        # Make sure reverse_lazy() is evaluated, as Python 3 won't do this here.
        self.base_url = force_text(self.base_url)
        return super(PrivateFileSystemStorage, self).url(name)
