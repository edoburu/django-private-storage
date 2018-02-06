import os

from django.db import models
from django.utils.text import slugify

from private_storage.fields import PrivateFileField


class SimpleDossier(models.Model):
    file = PrivateFileField()


class UploadToDossier(models.Model):
    file = PrivateFileField(upload_to='UploadToDossier')


class UploadToCallableDossier(models.Model):
    def upload_to(self, filename):
        return 'UploadToCallableDossier/test/' + filename

    file = PrivateFileField(upload_to=upload_to)


class CustomerDossier(models.Model):

    def upload_subfolder(self):
        # self.pk is still None here!
        return [slugify(self.customer)]

    customer = models.CharField(max_length=100)
    file = PrivateFileField(upload_to='CustomerDossier', upload_subfolder=upload_subfolder)


class CustomerDossierJoin(models.Model):

    def upload_subfolder2(self):
        # Slightly incorrect usage by developers, joining locally.
        return os.path.join(slugify(self.customer), 'sub2')

    customer = models.CharField(max_length=100)
    file = PrivateFileField(upload_to='CustomerDossierJoin', upload_subfolder=upload_subfolder2)
