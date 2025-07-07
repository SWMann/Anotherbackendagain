# backend/apps/units/management/commands/create_uee_ranks.py

from django.core.management.base import BaseCommand
from apps.units.models import Rank, Branch


class Command(BaseCommand):
    help = 'Deletes all existing ranks and creates UEE Military rank structure'

    def handle(self, *args, **options):
        # Delete all existing ranks
        self.stdout.write(self.style.WARNING('Deleting all existing ranks...'))
        deleted_count = Rank.objects.all().delete()[0]
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} existing ranks'))

        # Get or create UEE branch (assuming it exists or we'll create it)
        uee_branch, created = Branch.objects.get_or_create(
            name='United Empire of Earth Navy',
            defaults={
                'abbreviation': 'UEE',
                'description': 'The naval force of the United Empire of Earth',
                'color_code': '#0066CC'  # Navy blue
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created UEE branch'))
        else:
            self.stdout.write(self.style.SUCCESS('Using existing UEE branch'))

        # Define UEE rank data
        uee_ranks = [
            # Enlisted Ranks (tier 1-5)
            {
                'name': 'Applicant',
                'abbreviation': 'APP',
                'tier': 1,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 0,
                'min_time_in_grade': 0,
                'description': 'Initial applicant status'
            },
            {
                'name': 'Starman Recruit',
                'abbreviation': 'NRct',
                'tier': 2,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 0,
                'min_time_in_grade': 30,  # 30 days
                'description': 'Basic enlisted recruit'
            },
            {
                'name': 'Starman',
                'abbreviation': 'Strm',
                'tier': 3,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 90,
                'min_time_in_grade': 90,
                'description': 'Basic enlisted rank'
            },
            {
                'name': 'Able Starman',
                'abbreviation': 'AStrm',
                'tier': 4,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 180,
                'min_time_in_grade': 120,
                'description': 'Experienced enlisted personnel'
            },
            {
                'name': 'Leading Starman',
                'abbreviation': 'LStrm',
                'tier': 5,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 365,
                'min_time_in_grade': 180,
                'description': 'Senior enlisted, junior leadership'
            },

            # Non-Commissioned Officers (tier 6-9)
            {
                'name': 'Junior Petty Officer',
                'abbreviation': 'JPO',
                'tier': 6,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 730,  # 2 years
                'min_time_in_grade': 180,
                'description': 'Junior NCO rank'
            },
            {
                'name': 'Petty Officer',
                'abbreviation': 'PO',
                'tier': 7,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 1095,  # 3 years
                'min_time_in_grade': 365,
                'description': 'Standard NCO rank'
            },
            {
                'name': 'Chief Petty Officer',
                'abbreviation': 'CPO',
                'tier': 8,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 1825,  # 5 years
                'min_time_in_grade': 365,
                'description': 'Senior NCO rank'
            },
            {
                'name': 'Master Chief Petty Officer',
                'abbreviation': 'MCPO',
                'tier': 9,
                'is_enlisted': True,
                'is_officer': False,
                'is_warrant': False,
                'min_time_in_service': 2555,  # 7 years
                'min_time_in_grade': 730,
                'description': 'Highest NCO rank'
            },

            # Warrant Officers (tier 10-13)
            {
                'name': 'Warrant Officer Cadet',
                'abbreviation': 'WOC',
                'tier': 10,
                'is_enlisted': False,
                'is_officer': False,
                'is_warrant': True,
                'min_time_in_service': 1095,  # 3 years
                'min_time_in_grade': 0,
                'description': 'Warrant officer trainee'
            },
            {
                'name': 'Warrant Officer',
                'abbreviation': 'WO',
                'tier': 11,
                'is_enlisted': False,
                'is_officer': False,
                'is_warrant': True,
                'min_time_in_service': 1460,  # 4 years
                'min_time_in_grade': 180,
                'description': 'Basic warrant officer'
            },
            {
                'name': 'Senior Warrant Officer',
                'abbreviation': 'SWO',
                'tier': 12,
                'is_enlisted': False,
                'is_officer': False,
                'is_warrant': True,
                'min_time_in_service': 2190,  # 6 years
                'min_time_in_grade': 365,
                'description': 'Senior warrant officer'
            },
            {
                'name': 'Chief Warrant Officer',
                'abbreviation': 'CWO',
                'tier': 13,
                'is_enlisted': False,
                'is_officer': False,
                'is_warrant': True,
                'min_time_in_service': 2920,  # 8 years
                'min_time_in_grade': 730,
                'description': 'Highest warrant officer rank'
            },

            # Company Grade Officers (tier 14-17)
            {
                'name': 'Officer Cadet',
                'abbreviation': 'OCdt',
                'tier': 14,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 0,
                'min_time_in_grade': 0,
                'description': 'Officer trainee'
            },
            {
                'name': 'Ensign',
                'abbreviation': 'Ens',
                'tier': 15,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 0,
                'min_time_in_grade': 365,
                'description': 'Junior commissioned officer'
            },
            {
                'name': 'Lieutenant Junior Grade',
                'abbreviation': 'LTJG',
                'tier': 16,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 730,  # 2 years
                'min_time_in_grade': 365,
                'description': 'Junior lieutenant'
            },
            {
                'name': 'Lieutenant',
                'abbreviation': 'LT',
                'tier': 17,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 1460,  # 4 years
                'min_time_in_grade': 730,
                'description': 'Company grade officer'
            },

            # Field Grade Officers (tier 18-20)
            {
                'name': 'Lieutenant Commander',
                'abbreviation': 'LCDR',
                'tier': 18,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 2190,  # 6 years
                'min_time_in_grade': 1095,
                'description': 'Junior field grade officer'
            },
            {
                'name': 'Commander',
                'abbreviation': 'CDR',
                'tier': 19,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 3285,  # 9 years
                'min_time_in_grade': 1095,
                'description': 'Field grade officer'
            },
            {
                'name': 'Captain',
                'abbreviation': 'CAPT',
                'tier': 20,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 4380,  # 12 years
                'min_time_in_grade': 1460,
                'description': 'Senior field grade officer'
            },

            # High Command (tier 21-25)
            {
                'name': 'Commodore',
                'abbreviation': 'CDRE',
                'tier': 21,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 5475,  # 15 years
                'min_time_in_grade': 1825,
                'description': 'Junior flag officer'
            },
            {
                'name': 'Rear Admiral',
                'abbreviation': 'RADM',
                'tier': 22,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 6570,  # 18 years
                'min_time_in_grade': 1825,
                'description': 'Flag officer'
            },
            {
                'name': 'Vice Admiral',
                'abbreviation': 'VADM',
                'tier': 23,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 7665,  # 21 years
                'min_time_in_grade': 1825,
                'description': 'Senior flag officer'
            },
            {
                'name': 'Admiral',
                'abbreviation': 'ADM',
                'tier': 24,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 9125,  # 25 years
                'min_time_in_grade': 2190,
                'description': 'Four-star admiral'
            },
            {
                'name': 'Grand Admiral',
                'abbreviation': 'GADM',
                'tier': 25,
                'is_enlisted': False,
                'is_officer': True,
                'is_warrant': False,
                'min_time_in_service': 10950,  # 30 years
                'min_time_in_grade': 2555,
                'description': 'Highest naval rank'
            },
        ]

        # Create ranks
        created_count = 0
        for rank_data in uee_ranks:
            rank = Rank.objects.create(
                name=rank_data['name'],
                abbreviation=rank_data['abbreviation'],
                branch=uee_branch,
                tier=rank_data['tier'],
                description=rank_data['description'],
                is_officer=rank_data['is_officer'],
                is_enlisted=rank_data['is_enlisted'],
                is_warrant=rank_data['is_warrant'],
                min_time_in_service=rank_data['min_time_in_service'],
                min_time_in_grade=rank_data['min_time_in_grade'],
                color_code=self._get_color_code(rank_data)
            )
            created_count += 1
            self.stdout.write(f'Created rank: {rank.abbreviation} - {rank.name}')

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} UEE ranks'))
        self.stdout.write(self.style.SUCCESS(f'Enlisted ranks: {len([r for r in uee_ranks if r["is_enlisted"]])}'))
        self.stdout.write(
            self.style.SUCCESS(f'Warrant Officer ranks: {len([r for r in uee_ranks if r["is_warrant"]])}'))
        self.stdout.write(self.style.SUCCESS(f'Officer ranks: {len([r for r in uee_ranks if r["is_officer"]])}'))

    def _get_color_code(self, rank_data):
        """Return appropriate color code based on rank type"""
        if rank_data['tier'] <= 5:  # Enlisted
            return '#4CAF50'  # Green
        elif rank_data['tier'] <= 9:  # NCO
            return '#2196F3'  # Blue
        elif rank_data['tier'] <= 13:  # Warrant
            return '#9C27B0'  # Purple
        elif rank_data['tier'] <= 17:  # Company Grade
            return '#FF9800'  # Orange
        elif rank_data['tier'] <= 20:  # Field Grade
            return '#F44336'  # Red
        else:  # High Command
            return '#FFD700'  # Gold