# backend/apps/users/management/commands/create_bot_token.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates authentication tokens for the Discord bot'

    def handle(self, *args, **options):
        # First, let's check what fields are available
        self.stdout.write("Available User fields:")
        for field in User._meta.get_fields():
            self.stdout.write(f"  - {field.name}")

        # Create or get bot user with only the fields that exist
        bot_user, created = User.objects.get_or_create(
            discord_id='bot_5id',
            defaults={
                'username': 'Discord Bot',
                'email': 'bot@5id.mil',
                'is_staff': True,
                'is_admin': False,
                'is_active': True,

                # Only include fields that actually exist in your model
                'onboarding_status': 'Active',
                'recruit_status': False,
                'officer_candidate': False,
                'warrant_officer_candidate': False
            }
        )

        if created:
            # Set unusable password
            bot_user.set_unusable_password()
            bot_user.save()
            self.stdout.write(self.style.SUCCESS('Created new bot user'))
        else:
            self.stdout.write(self.style.SUCCESS('Using existing bot user'))

        # Generate tokens
        refresh = RefreshToken.for_user(bot_user)

        self.stdout.write(self.style.SUCCESS('\nBot authentication tokens:'))
        self.stdout.write(f'BOT_ACCESS_TOKEN={refresh.access_token}')
        self.stdout.write(f'BOT_REFRESH_TOKEN={refresh}')
        self.stdout.write('\nAdd these to your bot .env file')