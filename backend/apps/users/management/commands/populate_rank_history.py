# backend/apps/users/management/commands/populate_rank_history.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.units.models_promotion import UserRankHistory

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates rank history for users who have a rank but no rank history'

    def handle(self, *args, **options):
        users_with_rank = User.objects.filter(current_rank__isnull=False)
        created_count = 0

        self.stdout.write('Checking users with ranks...')

        for user in users_with_rank:
            # Check if user already has rank history
            has_history = UserRankHistory.objects.filter(user=user).exists()

            if not has_history and user.current_rank:
                # Create initial rank history entry
                UserRankHistory.objects.create(
                    user=user,
                    rank=user.current_rank,
                    date_assigned=user.join_date or timezone.now(),
                    notes='Initial rank history entry (populated by script)'
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created rank history for {user.username} - {user.current_rank.abbreviation}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} rank history entries'
            )
        )