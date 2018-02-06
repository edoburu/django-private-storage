#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import logging
import os
import posixpath
import warnings

import django
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import force_str, force_text
from django.utils.six import string_types
from django.utils.translation import ugettext_lazy as _

from .storage import private_storage

logger = logging.getLogger(__name__)


class PrivateFileField(models.FileField):
    """
    Filefield with private storage, custom filename and size checks.

    Extra settings:
    - ``upload_subfolder``: a lambda to find the subfolder, depending on the instance.
    - ``content_types``: list of allowed content types.
    - ``max_file_size``: maximum file size.
    """
    default_error_messages = {
        'invalid_file_type': _('File type not supported.'),
        'file_too_large': _('The file may not be larger then {max_size}.'),
    }

    def __init__(self, *args, **kwargs):
        self.upload_subfolder = kwargs.pop('upload_subfolder', None)
        self.content_types = kwargs.pop("content_types", None) or ()
        self.max_file_size = kwargs.pop("max_file_size", None)

        kwargs.setdefault('storage', private_storage)
        super(PrivateFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(PrivateFileField, self).clean(*args, **kwargs)
        file = data.file
        if isinstance(file, UploadedFile):
            # content_type is only available for uploaded files,
            # and not for files which are already stored in the model.
            content_type = file.content_type

            if self.content_types and content_type not in self.content_types:
                logger.debug('Rejected uploaded file type: %s', content_type)
                raise ValidationError(self.error_messages['invalid_file_type'])

            if self.max_file_size and file.size > self.max_file_size:
                raise ValidationError(self.error_messages['file_too_large'].format(
                    max_size=filesizeformat(self.max_file_size),
                    size=filesizeformat(file.size)
                ))

        return data

    def generate_filename(self, instance, filename):
        path_parts = []

        if self.upload_to:
            # Support the upload_to callable that Django provides
            if callable(self.upload_to):
                dirname, filename = os.path.split(self.upload_to(instance, filename))
                path_parts.append(dirname)
            else:
                dirname = force_text(datetime.datetime.now().strftime(force_str(self.upload_to)))
                path_parts.append(dirname)

        # Add our custom subdir function.
        upload_subfolder = self.upload_subfolder
        if upload_subfolder:
            # Should return a list, so joining can be done in a storage-specific manner.
            extra_dirs = upload_subfolder(instance)

            # Avoid mistakes by developers, no "s/u/b/p/a/t/h/"
            if isinstance(extra_dirs, string_types):
                warnings.warn("{}.{}.upload_subfolder should return a list"
                              " to avoid path-separator issues.".format(
                    instance.__class__.__name__, self.name), UserWarning)
                extra_dirs = os.path.split(extra_dirs)

            path_parts.extend([self.storage.get_valid_name(dir) for dir in extra_dirs])

        path_parts.append(self._get_clean_filename(filename))
        if django.VERSION >= (1, 10):
            filename = posixpath.join(*path_parts)
            return self.storage.generate_filename(filename)
        else:
            return os.path.join(*path_parts)

    def _get_clean_filename(self, filename):
        # As of Django 1.10+, file names are no longer cleaned locally, but cleaned by the storage.
        # This compatibility function makes sure all Django versions generate a safe filename.
        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))
