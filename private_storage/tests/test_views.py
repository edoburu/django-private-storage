from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from private_storage.tests.models import CustomerDossier
from private_storage.tests.utils import PrivateFileTestCase
from private_storage.views import PrivateStorageDetailView, PrivateStorageView


class ViewTests(PrivateFileTestCase):

    def test_detail_view(self):
        """
        Test the detail view that returns the object
        """
        CustomerDossier.objects.create(
            customer='cust1',
            file=SimpleUploadedFile('test4.txt', b'test4')
        )

        request = RequestFactory().get('/cust1/file/')
        request.user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

        # Initialize locally, no need for urls.py etc..
        # This behaves like a standard DetailView
        view = PrivateStorageDetailView.as_view(
            model=CustomerDossier,
            slug_url_kwarg='customer',
            slug_field='customer',
            model_file_field='file'
        )

        response = view(
            request,
            customer='cust1',
        )
        self.assertEqual(list(response.streaming_content), [b'test4'])
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Length'], '5')
        self.assertIn('Last-Modified', response)

    def test_private_file_view(self):
        """
        Test the detail view that returns the object
        """
        obj = CustomerDossier.objects.create(
            customer='cust2',
            file=SimpleUploadedFile('test5.txt', b'test5')
        )
        self.assertExists('CustomerDossier', 'cust2', 'test5.txt')

        request = RequestFactory().get('/cust1/file/')
        request.user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        request.META['HTTP_USER_AGENT'] = 'Test'

        # Initialize locally, no need for urls.py etc..
        # This behaves like a standard DetailView
        view = PrivateStorageView.as_view(
            content_disposition='attachment',
        )

        response = view(
            request,
            path='CustomerDossier/cust2/test5.txt'
        )
        self.assertEqual(list(response.streaming_content), [b'test5'])
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Length'], '5')
        self.assertEqual(response['Content-Disposition'], "attachment; filename*=UTF-8''test5.txt")
        self.assertIn('Last-Modified', response)
