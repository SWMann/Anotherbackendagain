# backend/apps/core/utils.py
from django.conf import settings
from urllib.parse import urljoin


def get_absolute_media_url(path, request=None):
    """
    Generate absolute media URL handling both Spaces and local storage.

    Args:
        path: Relative path to the media file
        request: Django request object (optional)

    Returns:
        Absolute URL to the media file
    """
    if not path:
        return None

    # If using Spaces, return the CDN URL
    if getattr(settings, 'USE_SPACES', False):
        # Path might already include /media/ prefix
        if path.startswith('/media/'):
            path = path[7:]  # Remove /media/ prefix
        elif path.startswith('media/'):
            path = path[6:]  # Remove media/ prefix

        return urljoin(settings.MEDIA_URL, path)

    # For local storage
    if request:
        # Build absolute URL using request
        media_url = urljoin(settings.MEDIA_URL, path)
        return request.build_absolute_uri(media_url)
    else:
        # Return relative URL with proper prefix
        return urljoin(settings.MEDIA_URL, path)


def ensure_absolute_url(url, request=None):
    """
    Ensure a URL is absolute. If it's relative, make it absolute.

    Args:
        url: The URL to check
        request: Django request object (optional)

    Returns:
        Absolute URL
    """
    if not url:
        return None

    # If already absolute, return as-is
    if url.startswith('http://') or url.startswith('https://'):
        return url

    # If request is provided, use it to build absolute URL
    if request:
        return request.build_absolute_uri(url)

    # Otherwise, just return the URL (it might be a Spaces URL)
    return url


def get_media_urls_dict(obj, field_names, request=None):
    """
    Get a dictionary of media URLs for multiple fields on an object.

    Args:
        obj: Model instance
        field_names: List of field names that contain media files
        request: Django request object (optional)

    Returns:
        Dictionary mapping field names to their absolute URLs
    """
    urls = {}

    for field_name in field_names:
        field = getattr(obj, field_name, None)
        if field and hasattr(field, 'url'):
            try:
                urls[field_name] = get_absolute_media_url(field.url, request)
            except ValueError:
                # No file associated with the field
                urls[field_name] = None
        else:
            urls[field_name] = None

    return urls


# Example usage in a view or serializer:
"""
from apps.core.utils import get_absolute_media_url

# In a serializer method
def get_avatar_url(self, obj):
    return get_absolute_media_url(
        obj.avatar.url if obj.avatar else None,
        self.context.get('request')
    )

# In a view
def get(self, request, pk=None):
    user = self.get_object()
    avatar_url = get_absolute_media_url(
        user.avatar.url if user.avatar else None,
        request
    )
    return Response({'avatar_url': avatar_url})
"""