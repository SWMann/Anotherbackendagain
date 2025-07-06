# backend/config/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    """
    Storage for static files (CSS, JS, images used in the app design)
    """
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True
    querystring_auth = False

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = getattr(
            settings,
            'SPACES_CDN_DOMAIN',
            f'{settings.AWS_STORAGE_BUCKET_NAME}.{settings.AWS_S3_REGION_NAME}.digitaloceanspaces.com'
        )
        super().__init__(*args, **kwargs)


class MediaStorage(S3Boto3Storage):
    """
    Storage for media files (user uploads like rank insignias, profile images, etc.)
    """
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False  # Don't overwrite files with same name
    querystring_auth = False  # Public URLs without auth parameters

    def __init__(self, *args, **kwargs):
        kwargs['custom_domain'] = getattr(
            settings,
            'SPACES_CDN_DOMAIN',
            f'{settings.AWS_STORAGE_BUCKET_NAME}.{settings.AWS_S3_REGION_NAME}.digitaloceanspaces.com'
        )
        super().__init__(*args, **kwargs)