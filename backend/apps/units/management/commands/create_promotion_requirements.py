# backend/apps/units/management/commands/create_promotion_requirements.py
"""
Create initial promotion requirements for UEE ranks
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.units.models import Rank, Role
from apps.units.models_promotion import (
    PromotionRequirementType, RankPromotionRequirement
)
from apps.training.models import TrainingCertificate


class Command(BaseCommand):
    help = 'Creates promotion requirement types and requirements for UEE ranks'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write('Creating promotion requirement types...')
            self._create_requirement_types()

            self.stdout.write('Creating rank promotion requirements...')
            self._create_rank_requirements()

            self.stdout.write(self.style.SUCCESS('Successfully created promotion requirements'))

    def _create_requirement_types(self):
        """Create the basic requirement types"""

        requirement_types = [
            # Time-based requirements
            {
                'name': 'Time in Service',
                'code': 'time_in_service',
                'category': 'time_based',
                'evaluation_type': 'time_in_service',
                'description': 'Total time served in the military'
            },
            {
                'name': 'Time in Grade',
                'code': 'time_in_grade',
                'category': 'time_based',
                'evaluation_type': 'time_in_grade',
                'description': 'Time served at current rank'
            },
            {
                'name': 'Time in Unit',
                'code': 'time_in_unit',
                'category': 'time_based',
                'evaluation_type': 'time_in_unit',
                'description': 'Time served in current unit'
            },
            {
                'name': 'Time in Position Type',
                'code': 'time_in_position_type',
                'category': 'position_based',
                'evaluation_type': 'time_in_position_type',
                'description': 'Time served in specific position types'
            },

            # Qualification-based requirements
            {
                'name': 'Required Certification',
                'code': 'certification_required',
                'category': 'qualification_based',
                'evaluation_type': 'certification_required',
                'description': 'Specific certification required'
            },
            {
                'name': 'Certification Count',
                'code': 'certifications_count',
                'category': 'qualification_based',
                'evaluation_type': 'certifications_count',
                'description': 'Number of certifications earned'
            },

            # Deployment-based requirements
            {
                'name': 'Deployment Count',
                'code': 'deployments_count',
                'category': 'deployment_based',
                'evaluation_type': 'deployments_count',
                'description': 'Number of combat deployments'
            },
            {
                'name': 'Deployment Time',
                'code': 'deployment_time',
                'category': 'deployment_based',
                'evaluation_type': 'deployment_time',
                'description': 'Total time spent on deployments'
            },

            # Leadership requirements
            {
                'name': 'Leadership Time',
                'code': 'leadership_time',
                'category': 'position_based',
                'evaluation_type': 'leadership_time',
                'description': 'Time in leadership positions'
            },
            {
                'name': 'Command Time',
                'code': 'command_time',
                'category': 'position_based',
                'evaluation_type': 'command_time',
                'description': 'Time in command positions'
            },

            # Performance requirements
            {
                'name': 'Performance Rating',
                'code': 'performance_rating',
                'category': 'performance_based',
                'evaluation_type': 'performance_rating',
                'description': 'Average performance rating'
            },
            {
                'name': 'Commendations',
                'code': 'commendations_count',
                'category': 'performance_based',
                'evaluation_type': 'commendations_count',
                'description': 'Number of commendations received'
            },

            # MOS requirements
            {
                'name': 'MOS Qualification Level',
                'code': 'mos_qualification',
                'category': 'qualification_based',
                'evaluation_type': 'mos_qualification',
                'description': 'MOS skill level requirement'
            },
        ]

        for req_type_data in requirement_types:
            req_type, created = PromotionRequirementType.objects.update_or_create(
                code=req_type_data['code'],
                defaults=req_type_data
            )
            if created:
                self.stdout.write(f'Created requirement type: {req_type.name}')
            else:
                self.stdout.write(f'Updated requirement type: {req_type.name}')

    def _create_rank_requirements(self):
        """Create specific requirements for each rank"""

        # Get requirement types
        time_in_service = PromotionRequirementType.objects.get(code='time_in_service')
        time_in_grade = PromotionRequirementType.objects.get(code='time_in_grade')
        time_in_unit = PromotionRequirementType.objects.get(code='time_in_unit')
        leadership_time = PromotionRequirementType.objects.get(code='leadership_time')
        command_time = PromotionRequirementType.objects.get(code='command_time')
        deployments = PromotionRequirementType.objects.get(code='deployments_count')
        cert_required = PromotionRequirementType.objects.get(code='certification_required')
        mos_qual = PromotionRequirementType.objects.get(code='mos_qualification')

        # Get UEE branch
        from apps.units.models import Branch
        uee_branch = Branch.objects.filter(abbreviation='UEE').first()
        if not uee_branch:
            self.stdout.write(self.style.ERROR('UEE branch not found!'))
            return

        # Define requirements for each rank
        rank_requirements = {
            # Enlisted Ranks
            'Strm': [  # Starman (E-3)
                (time_in_service, 90, "90 days time in service"),
                (time_in_grade, 90, "90 days as Starman Recruit"),
            ],
            'AStrm': [  # Able Starman (E-4)
                (time_in_service, 180, "180 days time in service"),
                (time_in_grade, 120, "120 days as Starman"),
                (deployments, 1, "At least 1 combat deployment"),
            ],
            'LStrm': [  # Leading Starman (E-5)
                (time_in_service, 365, "365 days time in service"),
                (time_in_grade, 180, "180 days as Able Starman"),
                (deployments, 3, "At least 3 combat deployments"),
                (time_in_unit, 90, "90 days in current unit"),
            ],

            # NCO Ranks
            'JPO': [  # Junior Petty Officer (E-6)
                (time_in_service, 730, "2 years time in service"),
                (time_in_grade, 180, "180 days as Leading Starman"),
                (deployments, 5, "At least 5 combat deployments"),
                (leadership_time, 90, "90 days in leadership position"),
                # Add Basic Leadership Course requirement when certs exist
            ],
            'PO': [  # Petty Officer (E-7)
                (time_in_service, 1095, "3 years time in service"),
                (time_in_grade, 365, "1 year as Junior Petty Officer"),
                (deployments, 8, "At least 8 combat deployments"),
                (leadership_time, 365, "1 year in leadership positions"),
                (mos_qual, 20, "MOS Skill Level 20"),
            ],
            'CPO': [  # Chief Petty Officer (E-8)
                (time_in_service, 1825, "5 years time in service"),
                (time_in_grade, 365, "1 year as Petty Officer"),
                (deployments, 12, "At least 12 combat deployments"),
                (leadership_time, 730, "2 years in leadership positions"),
                (mos_qual, 30, "MOS Skill Level 30"),
                # Add Advanced Leadership Course
            ],
            'MCPO': [  # Master Chief Petty Officer (E-9)
                (time_in_service, 2555, "7 years time in service"),
                (time_in_grade, 730, "2 years as Chief Petty Officer"),
                (deployments, 20, "At least 20 combat deployments"),
                (leadership_time, 1095, "3 years in leadership positions"),
                (command_time, 180, "180 days in command position"),
                (mos_qual, 40, "MOS Skill Level 40"),
            ],

            # Warrant Officer Ranks
            'WO': [  # Warrant Officer (W-2)
                (time_in_service, 1460, "4 years time in service"),
                (time_in_grade, 180, "180 days as Warrant Officer Cadet"),
                # Add Warrant Officer Basic Course
            ],
            'SWO': [  # Senior Warrant Officer (W-3)
                (time_in_service, 2190, "6 years time in service"),
                (time_in_grade, 365, "1 year as Warrant Officer"),
                (deployments, 10, "At least 10 combat deployments"),
            ],
            'CWO': [  # Chief Warrant Officer (W-4)
                (time_in_service, 2920, "8 years time in service"),
                (time_in_grade, 730, "2 years as Senior Warrant Officer"),
                (deployments, 15, "At least 15 combat deployments"),
                (leadership_time, 365, "1 year in leadership positions"),
            ],

            # Company Grade Officers
            'Ens': [  # Ensign (O-1)
                (time_in_grade, 365, "1 year as Officer Cadet"),
                # Add Officer Basic Course
            ],
            'LTJG': [  # Lieutenant Junior Grade (O-2)
                (time_in_service, 730, "2 years time in service"),
                (time_in_grade, 365, "1 year as Ensign"),
                (deployments, 2, "At least 2 combat deployments"),
            ],
            'LT': [  # Lieutenant (O-3)
                (time_in_service, 1460, "4 years time in service"),
                (time_in_grade, 730, "2 years as Lieutenant Junior Grade"),
                (deployments, 4, "At least 4 combat deployments"),
                (leadership_time, 365, "1 year in leadership positions"),
            ],

            # Field Grade Officers
            'LCDR': [  # Lieutenant Commander (O-4)
                (time_in_service, 2190, "6 years time in service"),
                (time_in_grade, 1095, "3 years as Lieutenant"),
                (deployments, 6, "At least 6 combat deployments"),
                (command_time, 180, "180 days in command position"),
                # Add Command and Staff Course
            ],
            'CDR': [  # Commander (O-5)
                (time_in_service, 3285, "9 years time in service"),
                (time_in_grade, 1095, "3 years as Lieutenant Commander"),
                (deployments, 10, "At least 10 combat deployments"),
                (command_time, 365, "1 year in command positions"),
            ],
            'CAPT': [  # Captain (O-6)
                (time_in_service, 4380, "12 years time in service"),
                (time_in_grade, 1460, "4 years as Commander"),
                (deployments, 15, "At least 15 combat deployments"),
                (command_time, 730, "2 years in command positions"),
                # Add Senior Service College
            ],

            # Flag Officers (simplified requirements)
            'CDRE': [  # Commodore (O-7)
                (time_in_service, 5475, "15 years time in service"),
                (time_in_grade, 1825, "5 years as Captain"),
                (command_time, 1095, "3 years in command positions"),
            ],
            'RADM': [  # Rear Admiral (O-8)
                (time_in_service, 6570, "18 years time in service"),
                (time_in_grade, 1825, "5 years as Commodore"),
                (command_time, 1460, "4 years in command positions"),
            ],
            'VADM': [  # Vice Admiral (O-9)
                (time_in_service, 7665, "21 years time in service"),
                (time_in_grade, 1825, "5 years as Rear Admiral"),
                (command_time, 1825, "5 years in command positions"),
            ],
            'ADM': [  # Admiral (O-10)
                (time_in_service, 9125, "25 years time in service"),
                (time_in_grade, 2190, "6 years as Vice Admiral"),
                (command_time, 2190, "6 years in command positions"),
            ],
            'GADM': [  # Grand Admiral (O-11)
                (time_in_service, 10950, "30 years time in service"),
                (time_in_grade, 2555, "7 years as Admiral"),
                (command_time, 2555, "7 years in command positions"),
            ],
        }

        # Create requirements for each rank
        for rank_abbr, requirements in rank_requirements.items():
            rank = Rank.objects.filter(
                abbreviation=rank_abbr,
                branch=uee_branch
            ).first()

            if not rank:
                self.stdout.write(self.style.WARNING(f'Rank {rank_abbr} not found'))
                continue

            display_order = 0
            for req_type, value, display_text in requirements:
                req_data = {
                    'rank': rank,
                    'requirement_type': req_type,
                    'value_required': value,
                    'display_text': display_text,
                    'is_mandatory': True,
                    'display_order': display_order,
                    'waiverable': req_type.code not in ['time_in_service', 'time_in_grade']
                }

                # Add specific fields based on requirement type
                if req_type.code == 'mos_qualification':
                    req_data['required_mos_level'] = value
                    req_data['value_required'] = 1  # Just need to have the level

                # Create or update requirement
                requirement, created = RankPromotionRequirement.objects.update_or_create(
                    rank=rank,
                    requirement_type=req_type,
                    defaults=req_data
                )

                if created:
                    self.stdout.write(f'Created requirement for {rank.name}: {display_text}')
                else:
                    self.stdout.write(f'Updated requirement for {rank.name}: {display_text}')

                display_order += 1