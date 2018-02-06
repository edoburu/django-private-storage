from django.db import models
from django.utils.text import slugify

from private_storage.fields import PrivateFileField


class SimpleDossier(models.Model):
    file = PrivateFileField()


class UploadToDossier(models.Model):
    file = PrivateFileField(upload_to='dossier2')


class CustomerDossier(models.Model):

    def upload_subfolder(self):
        # self.pk is still None here!
        return [slugify(self.customer)]

    customer = models.CharField(max_length=100)
    file = PrivateFileField(upload_to='dossier3', upload_subfolder=upload_subfolder)
