try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.utils.deconstruct import deconstructible

from private_storage import appconfig
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import setting


@deconstructible
class PrivateS3BotoStorage(S3Boto3Storage):
    """
    Private storage bucket for S3
    """

    access_key_names = ['AWS_PRIVATE_S3_ACCESS_KEY_ID', 'AWS_PRIVATE_ACCESS_KEY_ID'] + S3Boto3Storage.access_key_names
    secret_key_names = ['AWS_PRIVATE_S3_SECRET_ACCESS_KEY', 'AWS_PRIVATE_SECRET_ACCESS_KEY'] + S3Boto3Storage.secret_key_names

    # Since this class inherits the default storage, it shares many parameters with the base class.
    # Thus, redefine the setting name that is used to read these values, so almost all settings are not shared.
    access_key = setting('AWS_PRIVATE_S3_ACCESS_KEY_ID', setting('AWS_PRIVATE_ACCESS_KEY_ID', S3Boto3Storage.access_key))
    secret_key = setting('AWS_PRIVATE_S3_SECRET_ACCESS_KEY', setting('AWS_PRIVATE_SECRET_ACCESS_KEY', S3Boto3Storage.secret_key))
    file_overwrite = setting('AWS_PRIVATE_S3_FILE_OVERWRITE', False)  # false, differ from base class
    object_parameters = setting('AWS_PRIVATE_S3_OBJECT_PARAMETERS', {})
    bucket_name = setting('AWS_PRIVATE_STORAGE_BUCKET_NAME', strict=True)
    auto_create_bucket = setting('AWS_PRIVATE_AUTO_CREATE_BUCKET', False)
    default_acl = setting('AWS_PRIVATE_DEFAULT_ACL', 'private')  # differ from base class
    bucket_acl = setting('AWS_PRIVATE_BUCKET_ACL', default_acl)
    querystring_auth = setting('AWS_PRIVATE_QUERYSTRING_AUTH', True)
    querystring_expire = setting('AWS_PRIVATE_QUERYSTRING_EXPIRE', 3600)
    signature_version = setting('AWS_PRIVATE_S3_SIGNATURE_VERSION')
    reduced_redundancy = setting('AWS_PRIVATE_REDUCED_REDUNDANCY', False)
    location = setting('AWS_PRIVATE_LOCATION', '')
    encryption = setting('AWS_PRIVATE_S3_ENCRYPTION', False)
    custom_domain = setting('AWS_PRIVATE_S3_CUSTOM_DOMAIN')
    addressing_style = setting('AWS_PRIVATE_S3_ADDRESSING_STYLE')
    secure_urls = setting('AWS_PRIVATE_S3_SECURE_URLS', True)
    file_name_charset = setting('AWS_PRIVATE_S3_FILE_NAME_CHARSET', 'utf-8')
    gzip = setting('AWS_PRIVATE_IS_GZIPPED', S3Boto3Storage.gzip)  # fallback to default
    preload_metadata = setting('AWS_PRIVATE_PRELOAD_METADATA', False)
    url_protocol = setting('AWS_PRIVATE_S3_URL_PROTOCOL', S3Boto3Storage.url_protocol)  # fallback to default
    endpoint_url = setting('AWS_PRIVATE_S3_ENDPOINT_URL', None)
    region_name = setting('AWS_PRIVATE_S3_REGION_NAME', S3Boto3Storage.region_name)  # fallback to default
    use_ssl = setting('AWS_PRIVATE_S3_USE_SSL', True)

    def url(self, name, *args, **kwargs):
        if appconfig.PRIVATE_STORAGE_S3_REVERSE_PROXY or not self.querystring_auth:
            # There is no direct URL possible, return our streaming view instead.
            return reverse('serve_private_file', kwargs={'path': name})
        else:
            # The S3Boto3Storage can generate a presigned URL that is temporary available.
            return super(PrivateS3BotoStorage, self).url(name, *args, **kwargs)


@deconstructible
class PrivateEncryptedS3BotoStorage(PrivateS3BotoStorage):
    """
    Enforced encryption for private storage on S3.
    This is a convience option, it can also be implemented
    through :class:`PrivateS3BotoStorage` by using the proper settings.
    """
    encryption = True
    signature_version = PrivateS3BotoStorage.signature_version or 's3v4'
