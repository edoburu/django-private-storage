from django.core.files.uploadedfile import SimpleUploadedFile

from private_storage.tests.models import CustomerDossier, SimpleDossier, UploadToDossier
from private_storage.tests.utils import PrivateFileTestCase


class ModelTests(PrivateFileTestCase):

    def test_simple(self):
        SimpleDossier.objects.create(file=SimpleUploadedFile('test1.txt', b'test1'))
        self.assertExists('test1.txt')

    def test_upload_to(self):
        UploadToDossier.objects.create(file=SimpleUploadedFile('test2.txt', b'test2'))
        self.assertExists('dossier2', 'test2.txt')

    def test_upload_subfolder(self):
        obj = CustomerDossier.objects.create(customer='cust1', file=SimpleUploadedFile('test3.txt', b'test3'))
        self.assertExists('dossier3', 'cust1', 'test3.txt')
