try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from django.utils.deconstruct import deconstructible
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import setting

from private_storage import appconfig


@deconstructible
class PrivateS3BotoStorage(S3Boto3Storage):
    """
    Private storage bucket for S3
    """

    access_key_names = ['AWS_PRIVATE_S3_ACCESS_KEY_ID', 'AWS_PRIVATE_ACCESS_KEY_ID'] + S3Boto3Storage.access_key_names
    secret_key_names = ['AWS_PRIVATE_S3_SECRET_ACCESS_KEY', 'AWS_PRIVATE_SECRET_ACCESS_KEY'] + S3Boto3Storage.secret_key_names

    def __init__(self, **settings):
        super().__init__(**settings)
        self.file_overwrite = setting('AWS_PRIVATE_S3_FILE_OVERWRITE', False)  # false, differ from base class
        self.object_parameters = setting('AWS_PRIVATE_S3_OBJECT_PARAMETERS', {})
        self.bucket_name = setting('AWS_PRIVATE_STORAGE_BUCKET_NAME')
        self.auto_create_bucket = setting('AWS_PRIVATE_AUTO_CREATE_BUCKET', False)
        self.default_acl = setting('AWS_PRIVATE_DEFAULT_ACL', 'private')  # differ from base class
        self.bucket_acl = setting('AWS_PRIVATE_BUCKET_ACL', self.default_acl)
        self.querystring_auth = setting('AWS_PRIVATE_QUERYSTRING_AUTH', True)
        self.querystring_expire = setting('AWS_PRIVATE_QUERYSTRING_EXPIRE', 3600)
        self.signature_version = setting('AWS_PRIVATE_S3_SIGNATURE_VERSION')
        self.reduced_redundancy = setting('AWS_PRIVATE_REDUCED_REDUNDANCY', False)
        self.location = setting('AWS_PRIVATE_LOCATION', '')
        self.encryption = setting('AWS_PRIVATE_S3_ENCRYPTION', False)
        self.custom_domain = setting('AWS_PRIVATE_S3_CUSTOM_DOMAIN')
        self.addressing_style = setting('AWS_PRIVATE_S3_ADDRESSING_STYLE')
        self.secure_urls = setting('AWS_PRIVATE_S3_SECURE_URLS', True)
        self.file_name_charset = setting('AWS_PRIVATE_S3_FILE_NAME_CHARSET', 'utf-8')
        self.preload_metadata = setting('AWS_PRIVATE_PRELOAD_METADATA', False)
        self.endpoint_url = setting('AWS_PRIVATE_S3_ENDPOINT_URL', None)
        self.use_ssl = setting('AWS_PRIVATE_S3_USE_SSL', True)

        # default settings used to be class attributes on S3Boto3Storage, but
        # are now part of the initialization or moved to a dictionary
        self.access_key = setting('AWS_PRIVATE_S3_ACCESS_KEY_ID', setting('AWS_PRIVATE_ACCESS_KEY_ID', self.access_key))
        self.secret_key = setting('AWS_PRIVATE_S3_SECRET_ACCESS_KEY', setting('AWS_PRIVATE_SECRET_ACCESS_KEY', self.secret_key))
        if hasattr(self, "get_default_settings"):
            default_settings = self.get_default_settings()
            self.gzip = setting('AWS_PRIVATE_IS_GZIPPED', default_settings["gzip"])  # fallback to default
            self.url_protocol = setting('AWS_PRIVATE_S3_URL_PROTOCOL', default_settings["url_protocol"])  # fallback to default
            self.region_name = setting('AWS_PRIVATE_S3_REGION_NAME', default_settings["region_name"])  # fallback to default
        else:  # backward compatibility
            self.gzip = setting('AWS_PRIVATE_IS_GZIPPED', self.gzip)
            self.url_protocol = setting('AWS_PRIVATE_S3_URL_PROTOCOL', self.url_protocol)
            self.region_name = setting('AWS_PRIVATE_S3_REGION_NAME', self.region_name)
            


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

    def __init__(self, **settings):
        super().__init__(**settings)
        self.signature_version = self.signature_version or 's3v4'
