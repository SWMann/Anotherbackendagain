# backend/apps/core/management/commands/test_spaces.py
# Create this file to test Spaces configuration

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import boto3
from botocore.exceptions import ClientError
import io
from PIL import Image
import datetime


class Command(BaseCommand):
    help = 'Test Digital Ocean Spaces configuration and upload'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("DIGITAL OCEAN SPACES CONFIGURATION TEST")
        self.stdout.write("=" * 60 + "\n")

        # Step 1: Check configuration
        self.stdout.write(self.style.WARNING("\n1. Checking Configuration:"))
        config_ok = True

        settings_to_check = [
            ('USE_SPACES', False),
            ('AWS_ACCESS_KEY_ID', None),
            ('AWS_SECRET_ACCESS_KEY', None),
            ('AWS_STORAGE_BUCKET_NAME', None),
            ('AWS_S3_REGION_NAME', 'nyc3'),
            ('AWS_S3_ENDPOINT_URL', None),
            ('DEFAULT_FILE_STORAGE', None),
        ]

        for setting_name, default in settings_to_check:
            value = getattr(settings, setting_name, default)
            if value:
                if 'SECRET' in setting_name or 'KEY' in setting_name:
                    display_value = f"{'*' * 10} (hidden)"
                else:
                    display_value = value
                self.stdout.write(f"✓ {setting_name}: {display_value}")
            else:
                self.stdout.write(self.style.ERROR(f"✗ {setting_name}: Not set"))
                config_ok = False

        if not config_ok:
            self.stdout.write(
                self.style.ERROR("\n❌ Configuration incomplete. Please set all required environment variables."))
            return

        # Step 2: Test connection
        self.stdout.write(self.style.WARNING("\n2. Testing Connection:"))
        try:
            client = boto3.client(
                's3',
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            # List buckets
            response = client.list_buckets()
            self.stdout.write(self.style.SUCCESS(f"✓ Connected successfully! Found {len(response['Buckets'])} buckets"))

            # Check if our bucket exists
            bucket_exists = False
            for bucket in response['Buckets']:
                if bucket['Name'] == settings.AWS_STORAGE_BUCKET_NAME:
                    bucket_exists = True
                    self.stdout.write(f"  - {bucket['Name']} ✓ (target bucket)")
                else:
                    self.stdout.write(f"  - {bucket['Name']}")

            if not bucket_exists:
                self.stdout.write(self.style.ERROR(f"\n❌ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' not found!"))
                return

        except ClientError as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Connection failed: {e.response['Error']['Message']}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Unexpected error: {str(e)}"))
            return

        # Step 3: Test upload permissions
        self.stdout.write(self.style.WARNING("\n3. Testing Upload Permissions:"))
        try:
            test_content = b"Digital Ocean Spaces test file"
            test_key = f"test/test_upload_{datetime.datetime.now().isoformat()}.txt"

            client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=test_key,
                Body=test_content,
                ACL='public-read'
            )
            self.stdout.write(self.style.SUCCESS("✓ Upload permission test passed"))

            # Try to read it back
            obj = client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=test_key)
            self.stdout.write(self.style.SUCCESS("✓ Read permission test passed"))

            # Delete test file
            client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=test_key)
            self.stdout.write(self.style.SUCCESS("✓ Delete permission test passed"))

        except ClientError as e:
            self.stdout.write(self.style.ERROR(f"✗ Permission test failed: {e.response['Error']['Message']}"))
            return

        # Step 4: Test Django storage backend
        self.stdout.write(self.style.WARNING("\n4. Testing Django Storage Backend:"))
        self.stdout.write(f"Storage class: {default_storage.__class__.__name__}")
        self.stdout.write(f"Storage module: {default_storage.__class__.__module__}")

        try:
            # Create a test image
            img = Image.new('RGB', (100, 100), color='red')
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)

            # Save via Django storage
            test_file_name = f"test/django_test_{datetime.datetime.now().isoformat()}.jpg"
            saved_name = default_storage.save(test_file_name, ContentFile(img_io.read()))
            self.stdout.write(self.style.SUCCESS(f"✓ File saved as: {saved_name}"))

            # Get URL
            file_url = default_storage.url(saved_name)
            self.stdout.write(self.style.SUCCESS(f"✓ File URL: {file_url}"))

            # Check if file exists
            exists = default_storage.exists(saved_name)
            self.stdout.write(self.style.SUCCESS(f"✓ File exists check: {exists}"))

            # Get file size
            size = default_storage.size(saved_name)
            self.stdout.write(self.style.SUCCESS(f"✓ File size: {size} bytes"))

            # Clean up
            default_storage.delete(saved_name)
            self.stdout.write(self.style.SUCCESS("✓ Test file deleted"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Django storage test failed: {str(e)}"))
            import traceback
            traceback.print_exc()
            return

        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("✓ ALL TESTS PASSED! Spaces is configured correctly."))
        self.stdout.write(self.style.SUCCESS("=" * 60 + "\n"))

        # Provide example URLs
        self.stdout.write("\nExample URLs for your setup:")
        self.stdout.write(f"Static files: https://{settings.AWS_S3_CUSTOM_DOMAIN}/static/")
        self.stdout.write(f"Media files: https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/")
        self.stdout.write(f"\nMake sure to add your frontend domain to Spaces CORS settings!")

# To run this command:
# python manage.py test_spaces