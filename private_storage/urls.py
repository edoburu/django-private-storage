from django.conf.urls import url

from .views import PrivateStorageView

urlpatterns = [
    url(r'^(?P<path>.*)$', PrivateStorageView.as_view(), name='serve_private_file'),
]
