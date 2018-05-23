from django.test import RequestFactory, SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from private_storage.models import PrivateFile
from private_storage.storage import private_storage
from private_storage.tests.models import CustomerDossier, CustomerDossierJoin, SimpleDossier, \
    UploadToCallableDossier, UploadToDossier
from private_storage.tests.utils import PrivateFileTestCase


class ModelTests(PrivateFileTestCase):

    def test_simple(self):
        SimpleDossier.objects.create(file=SimpleUploadedFile('test1.txt', b'test1'))
        self.assertExists('test1.txt')

    def test_upload_to(self):
        UploadToDossier.objects.create(file=SimpleUploadedFile('test2.txt', b'test2'))
        self.assertExists('UploadToDossier', 'test2.txt')

    def test_upload_to_callable(self):
        UploadToCallableDossier.objects.create(file=SimpleUploadedFile('test7.txt', b'test7'))
        self.assertExists('UploadToCallableDossier', 'test', 'test7.txt')

    def test_upload_subfolder(self):
        obj = CustomerDossier.objects.create(customer='cust1', file=SimpleUploadedFile('test3.txt', b'test3'))
        self.assertExists('CustomerDossier', 'cust1', 'test3.txt')

    def test_upload_subfolder_join(self):
        obj = CustomerDossierJoin.objects.create(customer='cust4', file=SimpleUploadedFile('test6.txt', b'test6'))
        self.assertExists('CustomerDossierJoin', 'cust4', 'sub2', 'test6.txt')


class PrivateFileTests(SimpleTestCase):
    def test_privatefile_exists_none(self):
        # Retrieving a FieldFile(none) should not give errors
        request = RequestFactory().get('/')
        self.assertFalse(PrivateFile(request, private_storage, None).exists())
