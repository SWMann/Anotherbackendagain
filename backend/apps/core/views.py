# Common view mixins can go here if needed 

# backend/apps/core/views.py
# Add this debug view

from django.http import JsonResponse
from django.conf import settings
import os
from pathlib import Path
from rest_framework import viewsets


def debug_static_config(request):
    """Debug static files configuration"""
    static_root = Path(settings.STATIC_ROOT)

    # Check if admin CSS exists
    admin_css_path = static_root / 'admin' / 'css' / 'base.css'
    admin_css_exists = admin_css_path.exists()

    # List files in static root
    static_files_count = 0
    admin_files_count = 0
    if static_root.exists():
        static_files_count = sum(1 for _ in static_root.rglob('*') if _.is_file())
        admin_dir = static_root / 'admin'
        if admin_dir.exists():
            admin_files_count = sum(1 for _ in admin_dir.rglob('*') if _.is_file())

    return JsonResponse({
        'environment': {
            'debug': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'on_digital_ocean': os.environ.get('DIGITAL_OCEAN', 'not set'),
        },
        'static_configuration': {
            'STATIC_URL': settings.STATIC_URL,
            'STATIC_ROOT': str(settings.STATIC_ROOT),
            'STATICFILES_STORAGE': settings.STATICFILES_STORAGE,
            'FORCE_SCRIPT_NAME': getattr(settings, 'FORCE_SCRIPT_NAME', 'not set'),
            'WHITENOISE_STATIC_PREFIX': getattr(settings, 'WHITENOISE_STATIC_PREFIX', 'not set'),
        },
        'static_files_check': {
            'static_root_exists': static_root.exists(),
            'admin_css_exists': admin_css_exists,
            'admin_css_path': str(admin_css_path),
            'total_static_files': static_files_count,
            'admin_static_files': admin_files_count,
        },
        'middleware_check': {
            'has_whitenoise': any('whitenoise' in m.lower() for m in settings.MIDDLEWARE),
            'whitenoise_position': [i for i, m in enumerate(settings.MIDDLEWARE) if 'whitenoise' in m.lower()],
        },
        'request_info': {
            'path': request.path,
            'full_path': request.get_full_path(),
            'host': request.get_host(),
            'scheme': request.scheme,
        }
    }, json_dumps_params={'indent': 2})




class MediaContextMixin:
    """
    Mixin to ensure serializers always get request context
    for proper media URL generation.
    """

    def get_serializer_context(self):
        """
        Add request to serializer context.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
