import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from private_storage.tests.models import CustomerDossier, SimpleDossier, UploadToDossier


class PrivateFileTestCase(TestCase):

    def tearDown(self):
        """
        Empty the test folder after each test case.
        """
        super(PrivateFileTestCase, self).tearDown()
        shutil.rmtree(settings.PRIVATE_STORAGE_ROOT)

    def assertExists(self, *parts):
        """
        Extra assert, check whether a path exists.
        """
        path = os.path.join(settings.PRIVATE_STORAGE_ROOT, *parts)
        if not os.path.exists(path):
            raise self.failureException("Path {} does not exist".format(path))


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
