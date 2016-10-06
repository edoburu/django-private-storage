"""
Django Storage interface
"""
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse_lazy
from . import appconfig

__all__ = (
    'private_storage',
    'PrivateStorage',
)


class PrivateStorage(FileSystemStorage):
    """
    Interface to the Django storage system,
    storing the files in a private folder.
    """
    def __init__(self, location=None, base_url=None, **kwargs):
        if location is None:
            location = appconfig.PRIVATE_STORAGE_ROOT

        super(PrivateStorage, self).__init__(
            location=location,
            base_url=base_url,
            **kwargs
        )
        if base_url is None:
            # When base_url is not given, it's autodetected.
            # However, as the super method checks for base_url.endswith('/'),
            # the attribute is overwritten here to avoid breaking lazy evaluation.
            self.base_url = reverse_lazy('serve_private_file', kwargs={'path': ''})


# Singleton instance.
private_storage = PrivateStorage()
