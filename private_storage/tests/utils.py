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
            all_files = []
            for root, dirs, files in os.walk(settings.PRIVATE_STORAGE_ROOT):
                all_files.extend([os.path.join(root, file) for file in files])
            all_files.sort()
            raise self.failureException("Path {} does not exist, found:\n{}".format(
                path,
                "\n".join(all_files)
            ))
