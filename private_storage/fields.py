#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from .storage import private_storage


class PrivateFileField(models.FileField):
    """
    Filefield with private storage, custom filename and size checks.

    Extra settings:
    - ``upload_subfolder``: a lambda to find the subfolder, depending on the instance.
    - ``content_types``: list of allowed content types.
    - ``max_file_size``: maximum file size.
    """

    def __init__(self, *args, **kwargs):
        self._upload = kwargs.pop('upload_subfolder', None)
        self.content_types = kwargs.pop("content_types", None) or ()
        self.max_file_size = kwargs.pop("max_file_size", None)

        kwargs.setdefault('storage', private_storage)
        if self._upload:
            kwargs.setdefault('upload_to', 'uploads')  # shut up warnings from Django 1.6- model validation
        super(PrivateFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(PrivateFileField, self).clean(*args, **kwargs)
        file = data.file
        if isinstance(file, UploadedFile):
            # content_type is only available for uploaded files,
            # and not for files which are already stored in the model.
            content_type = file.content_type

            if self.content_types and content_type not in self.content_types:
                raise ValidationError(_('Filetype not supported.'))

            if self.max_file_size and file.size > self.max_file_size:
                raise ValidationError(_('Please keep the file size under {max_size}, the uploaded file is {cur_size}').format(
                    max_size=filesizeformat(self.max_upload_size),
                    cur_size=filesizeformat(file.size)
                ))

        return data

    def generate_filename(self, instance, filename):
        subdir_func = self._upload
        if subdir_func:
            subdirs = [self.storage.get_valid_name(dir) for dir in subdir_func(instance)]
        else:
            subdirs = [self.upload_to]

        if not subdirs:
            subdirs = [self.get_directory_name()]
        dirs = list(subdirs) + [self.get_filename(filename)]
        return smart_str(os.path.join(*dirs))
