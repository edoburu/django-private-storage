import minio

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from minio_storage.policy import Policy
from minio_storage.storage import MinioStorage

from private_storage import appconfig

_NoValue = object()


def default_setting(name, default=_NoValue):
    result = getattr(settings, name, default)
    if result is _NoValue:
        raise ImproperlyConfigured
    else:
        return result


def private_or_default_setting(private_name, default_name, default_value=_NoValue):
    result = getattr(settings, private_name, None)
    if not result:
        return default_setting(default_name, default_value)
    else:
        return result


class PrivateMinioStorage(MinioStorage):
    def __init__(self):
        endpoint = private_or_default_setting("MINIO_PRIVATE_STORAGE_ENDPOINT", "MINIO_STORAGE_ENDPOINT")
        access_key = private_or_default_setting("MINIO_PRIVATE_STORAGE_ACCESS_KEY", "MINIO_STORAGE_ACCESS_KEY")
        secret_key = private_or_default_setting("MINIO_PRIVATE_STORAGE_SECRET_KEY", "MINIO_STORAGE_SECRET_KEY")
        secure = private_or_default_setting("MINIO_PRIVATE_STORAGE_USE_HTTPS", "MINIO_STORAGE_USE_HTTPS", True)

        bucket_name = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_MEDIA_BUCKET_NAME", "MINIO_STORAGE_MEDIA_BUCKET_NAME"
        )
        base_url = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_MEDIA_URL", "MINIO_STORAGE_MEDIA_URL", None
        )
        auto_create_bucket = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_AUTO_CREATE_MEDIA_BUCKET", "MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET", False
        )
        auto_create_policy = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_AUTO_CREATE_MEDIA_POLICY", "MINIO_STORAGE_AUTO_CREATE_MEDIA_POLICY", "GET_ONLY"
        )

        policy_type = Policy.get
        if isinstance(auto_create_policy, str):
            policy_type = Policy(auto_create_policy)
            auto_create_policy = True

        presign_urls = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_MEDIA_USE_PRESIGNED", "MINIO_STORAGE_MEDIA_USE_PRESIGNED", False
        )
        backup_format = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_MEDIA_BACKUP_FORMAT", "MINIO_STORAGE_MEDIA_BACKUP_FORMAT", False
        )
        backup_bucket = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_MEDIA_BACKUP_BUCKET", "MINIO_STORAGE_MEDIA_BACKUP_BUCKET", False
        )
        assume_bucket_exists = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_ASSUME_MEDIA_BUCKET_EXISTS", "MINIO_STORAGE_ASSUME_MEDIA_BUCKET_EXISTS", False
        )
        object_metadata = private_or_default_setting(
            "MINIO_PRIVATE_STORAGE_OBJECT_METADATA", "MINIO_STORAGE_MEDIA_OBJECT_METADATA", None
        )

        client = minio.Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

        super().__init__(
            client,
            bucket_name,
            auto_create_bucket=auto_create_bucket,
            auto_create_policy=auto_create_policy,
            policy_type=policy_type,
            base_url=base_url,
            presign_urls=presign_urls,
            backup_format=backup_format,
            backup_bucket=backup_bucket,
            assume_bucket_exists=assume_bucket_exists,
            object_metadata=object_metadata,
        )

    def get_modified_time(self, name):
        return self.modified_time(name)

    def url(self, name: str, *args, **kwargs) -> str:
        if appconfig.PRIVATE_STORAGE_MINO_REVERSE_PROXY:
            return reverse('serve_private_file', kwargs={'path': name})
        return super().url(name, *args, **kwargs)
