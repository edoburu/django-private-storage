from django.urls import re_path

from .views import PrivateStorageView

urlpatterns = [
    re_path(r'^(?P<path>.*)$', PrivateStorageView.as_view(), name='serve_private_file'),
]
