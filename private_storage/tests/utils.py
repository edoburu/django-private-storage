import os
import shutil

from django.conf import settings
from django.test import TestCase


class PrivateFileTestCase(TestCase):

    def tearDown(self):
        """
        Empty the test folder after each test case.
        """
        super(PrivateFileTestCase, self).tearDown()
        if os.path.exists(settings.PRIVATE_STORAGE_ROOT):
            shutil.rmtree(settings.PRIVATE_STORAGE_ROOT)

    def assertExists(self, *parts):
        """
        Extra assert, check whether a path exists.
        """
        path = os.path.join(settings.PRIVATE_STORAGE_ROOT, *parts)
        if not os.path.exists(path):
            raise self.failureException("Path {} does not exist".format(path))
