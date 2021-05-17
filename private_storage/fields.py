#-*- coding: utf-8 -*-
import datetime
import logging
import os
import posixpath
import warnings

import django
from django.core import checks
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.db.models.fields.files import ImageFieldFile, ImageFileDescriptor
from django.forms import ImageField
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import force_str, force_text
from django.utils.translation import gettext_lazy as _

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
        'file_too_large': _('The file may not be larger than {max_size}.'),
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
            if isinstance(extra_dirs, str):
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


class PrivateImageField(PrivateFileField):
    attr_class = ImageFieldFile
    descriptor_class = ImageFileDescriptor
    description = _("Image")

    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        self.width_field, self.height_field = width_field, height_field
        super().__init__(verbose_name, name, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_image_library_installed(),
        ]

    def _check_image_library_installed(self):
        try:
            from PIL import Image  # NOQA
        except ImportError:
            return [
                checks.Error(
                    'Cannot use ImageField because Pillow is not installed.',
                    hint=('Get Pillow at https://pypi.org/project/Pillow/ '
                          'or run command "python -m pip install Pillow".'),
                    obj=self,
                    id='fields.E210',
                )
            ]
        else:
            return []

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.width_field:
            kwargs['width_field'] = self.width_field
        if self.height_field:
            kwargs['height_field'] = self.height_field
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        # Attach update_dimension_fields so that dimension fields declared
        # after their corresponding image field don't stay cleared by
        # Model.__init__, see bug #11196.
        # Only run post-initialization dimension update on non-abstract models
        if not cls._meta.abstract:
            models.signals.post_init.connect(self.update_dimension_fields, sender=cls)

    def update_dimension_fields(self, instance, force=False, *args, **kwargs):
        """
        Update field's width and height fields, if defined.

        This method is hooked up to model's post_init signal to update
        dimensions after instantiating a model instance.  However, dimensions
        won't be updated if the dimensions fields are already populated.  This
        avoids unnecessary recalculation when loading an object from the
        database.

        Dimensions can be forced to update with force=True, which is how
        ImageFileDescriptor.__set__ calls this method.
        """
        # Nothing to update if the field doesn't have dimension fields or if
        # the field is deferred.
        has_dimension_fields = self.width_field or self.height_field
        if not has_dimension_fields or self.attname not in instance.__dict__:
            return

        # getattr will call the ImageFileDescriptor's __get__ method, which
        # coerces the assigned value into an instance of self.attr_class
        # (ImageFieldFile in this case).
        file = getattr(instance, self.attname)

        # Nothing to update if we have no file and not being forced to update.
        if not file and not force:
            return

        dimension_fields_filled = not(
            (self.width_field and not getattr(instance, self.width_field)) or
            (self.height_field and not getattr(instance, self.height_field))
        )
        # When both dimension fields have values, we are most likely loading
        # data from the database or updating an image field that already had
        # an image stored.  In the first case, we don't want to update the
        # dimension fields because we are already getting their values from the
        # database.  In the second case, we do want to update the dimensions
        # fields and will skip this return because force will be True since we
        # were called from ImageFileDescriptor.__set__.
        if dimension_fields_filled and not force:
            return

        # file should be an instance of ImageFieldFile or should be None.
        if file:
            width = file.width
            height = file.height
        else:
            # No file, so clear dimensions fields.
            width = None
            height = None

        # Update the width and height fields.
        if self.width_field:
            setattr(instance, self.width_field, width)
        if self.height_field:
            setattr(instance, self.height_field, height)

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': ImageField,
            **kwargs,
        })
