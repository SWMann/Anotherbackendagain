# backend/apps/core/serializers.py
from rest_framework import serializers
from django.conf import settings


class MediaURLMixin:
    """
    Mixin to handle media URLs properly in serializers,
    accounting for URL prefix and Spaces CDN.
    """

    def get_media_url(self, obj, field_name):
        """
        Get the proper media URL for a file field.

        Args:
            obj: The model instance
            field_name: The name of the file field

        Returns:
            The complete URL for the media file
        """
        file_field = getattr(obj, field_name, None)

        if not file_field:
            return None

        # If we don't have a file, return None
        if not hasattr(file_field, 'url'):
            return None

        try:
            url = file_field.url

            # If using Spaces, the URL is already complete
            if getattr(settings, 'USE_SPACES', False):
                return url

            # For local storage, ensure we have the full URL
            request = self.context.get('request')
            if request and not url.startswith('http'):
                # Build absolute URL
                return request.build_absolute_uri(url)

            return url
        except ValueError:
            # File field exists but no file is actually stored
            return None

    def get_multiple_media_urls(self, obj, field_names):
        """
        Get media URLs for multiple fields.

        Args:
            obj: The model instance
            field_names: List of file field names

        Returns:
            Dictionary mapping field names to URLs
        """
        urls = {}
        for field_name in field_names:
            urls[field_name] = self.get_media_url(obj, field_name)
        return urls



# Common serializers can go here if needed
