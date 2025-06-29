# backend/apps/users/management/commands/create_admin.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates an admin user for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--discord-id',
            default='admin',
            help='Discord ID for the admin user'
        )
        parser.add_argument(
            '--username',
            default='admin',
            help='Username for the admin user'
        )
        parser.add_argument(
            '--email',
            default='admin@example.com',
            help='Email for the admin user'
        )
        parser.add_argument(
            '--password',
            default='admin123',
            help='Password for the admin user'
        )

    def handle(self, *args, **options):
        discord_id = options['discord_id']
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(discord_id=discord_id).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user with discord_id "{discord_id}" already exists')
            )
            # Update the existing user's password
            user = User.objects.get(discord_id=discord_id)
            user.set_password(password)
            user.is_admin = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated password for admin user "{discord_id}"')
            )
        else:
            user = User.objects.create_superuser(
                discord_id=discord_id,
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user "{discord_id}"')
            )