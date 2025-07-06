# backend/config/storage_backends.py
# Fixed version with better error handling and debugging

from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class StaticStorage(S3Boto3Storage):
    """
    Storage for static files (CSS, JS, images used in the app design)
    """
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True
    querystring_auth = False

    def __init__(self, *args, **kwargs):
        # Use the CDN domain if available
        kwargs['custom_domain'] = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
        super().__init__(*args, **kwargs)

        # Log configuration for debugging
        logger.info(f"StaticStorage initialized with domain: {kwargs.get('custom_domain')}")


class MediaStorage(S3Boto3Storage):
    """
    Storage for media files (user uploads like rank insignias, profile images, etc.)
    """
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False  # Don't overwrite files with same name
    querystring_auth = False  # Public URLs without auth parameters

    # Explicitly set these to ensure proper configuration
    access_key = settings.AWS_ACCESS_KEY_ID if hasattr(settings, 'AWS_ACCESS_KEY_ID') else None
    secret_key = settings.AWS_SECRET_ACCESS_KEY if hasattr(settings, 'AWS_SECRET_ACCESS_KEY') else None
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') else None
    endpoint_url = settings.AWS_S3_ENDPOINT_URL if hasattr(settings, 'AWS_S3_ENDPOINT_URL') else None
    region_name = settings.AWS_S3_REGION_NAME if hasattr(settings, 'AWS_S3_REGION_NAME') else 'nyc3'

    def __init__(self, *args, **kwargs):
        # Set custom domain for CDN
        if hasattr(settings, 'AWS_S3_CUSTOM_DOMAIN'):
            kwargs['custom_domain'] = settings.AWS_S3_CUSTOM_DOMAIN

        # Ensure we're using the correct endpoint
        if self.endpoint_url:
            kwargs['endpoint_url'] = self.endpoint_url

        super().__init__(*args, **kwargs)

        # Log configuration for debugging
        logger.info(f"MediaStorage initialized:")
        logger.info(f"  - Bucket: {self.bucket_name}")
        logger.info(f"  - Endpoint: {self.endpoint_url}")
        logger.info(f"  - Region: {self.region_name}")
        logger.info(f"  - Custom Domain: {kwargs.get('custom_domain', 'Not set')}")
        logger.info(f"  - Location: {self.location}")

    def _save(self, name, content):
        """
        Override save to add debugging
        """
        logger.info(f"Attempting to save file: {name}")
        logger.info(f"  - Content type: {getattr(content, 'content_type', 'Unknown')}")
        logger.info(f"  - Size: {getattr(content, 'size', 'Unknown')}")

        try:
            result = super()._save(name, content)
            logger.info(f"Successfully saved file: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to save file {name}: {str(e)}")
            raise

    def url(self, name):
        """
        Override URL generation to ensure correct URLs
        """
        url = super().url(name)
        logger.debug(f"Generated URL for {name}: {url}")
        return url