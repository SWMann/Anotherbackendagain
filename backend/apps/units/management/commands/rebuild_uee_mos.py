# backend/apps/units/management/commands/rebuild_uee_mos.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.units.models import MOS, Branch
import sys


class Command(BaseCommand):
    help = 'Deletes all existing MOS data and rebuilds it for UEE/Star Citizen'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )
        parser.add_argument(
            '--preserve-assignments',
            action='store_true',
            help='Attempt to preserve user MOS assignments where possible',
        )

    def handle(self, *args, **options):
        force = options['force']
        preserve = options['preserve_assignments']

        # Get counts before deletion
        existing_count = MOS.objects.count()

        if existing_count > 0 and not force:
            self.stdout.write(self.style.WARNING(
                f'\nThis will DELETE all {existing_count} existing MOS entries and rebuild them.'
            ))
            confirm = input('Are you sure you want to continue? Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        # Store existing assignments if preserving
        preserved_assignments = {}
        if preserve:
            self.stdout.write('Preserving existing MOS assignments...')
            from apps.users.models import User
            for user in User.objects.filter(primary_mos__isnull=False):
                preserved_assignments[user.id] = {
                    'primary_mos_code': user.primary_mos.code,
                    'secondary_mos_codes': [mos.code for mos in user.secondary_mos.all()]
                }
            self.stdout.write(f'Preserved {len(preserved_assignments)} user assignments')

        with transaction.atomic():
            # Delete all existing MOS data
            self.stdout.write('\nDeleting existing MOS data...')
            deleted_count = MOS.objects.count()
            MOS.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} MOS entries'))

            # Get or create branches
            self.stdout.write('\nVerifying UEE branches...')
            branches = {}
            branch_data = [
                ('UEEA', 'UEE Army'),
                ('UEEN', 'UEE Navy'),
                ('UEEM', 'UEE Marines'),
            ]

            for abbr, name in branch_data:
                branch, created = Branch.objects.get_or_create(
                    abbreviation=abbr,
                    defaults={'name': name}
                )
                branches[abbr] = branch
                if created:
                    self.stdout.write(f'Created branch: {name}')
                else:
                    self.stdout.write(f'Found branch: {name}')

            # Create all UEE MOS/Roles
            self.stdout.write('\nCreating UEE MOS/Role data...')

            mos_data = self.get_uee_mos_data(branches)
            created_count = 0
            created_mos = {}

            for role in mos_data:
                mos = MOS.objects.create(**role)
                created_count += 1
                created_mos[mos.code] = mos
                self.stdout.write(f'Created: {mos.code} - {mos.title}')

            # Restore assignments if preserving
            restored_count = 0
            if preserve and preserved_assignments:
                self.stdout.write('\nRestoring user MOS assignments...')
                from apps.users.models import User

                for user_id, assignments in preserved_assignments.items():
                    try:
                        user = User.objects.get(id=user_id)

                        # Restore primary MOS if it exists
                        if assignments['primary_mos_code'] in created_mos:
                            user.primary_mos = created_mos[assignments['primary_mos_code']]
                            user.save()
                            restored_count += 1

                        # Restore secondary MOS
                        for mos_code in assignments['secondary_mos_codes']:
                            if mos_code in created_mos:
                                user.secondary_mos.add(created_mos[mos_code])
                    except User.DoesNotExist:
                        pass

                self.stdout.write(f'Restored {restored_count} primary MOS assignments')

            # Summary
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Successfully rebuilt MOS data!'
                f'\n  - Deleted: {deleted_count} old entries'
                f'\n  - Created: {created_count} new UEE roles'
                f'\n  - Categories: {len(set(m["category"] for m in mos_data))}'
                f'\n  - Branches: {len(branches)}'
            ))

            # Show category breakdown
            self.stdout.write('\nMOS by Category:')
            categories = {}
            for mos in mos_data:
                cat = mos['category']
                categories[cat] = categories.get(cat, 0) + 1

            for cat, count in sorted(categories.items()):
                self.stdout.write(f'  {cat}: {count}')

    def get_uee_mos_data(self, branches):
        """Returns the complete UEE MOS/Role data"""
        return [
            # NAVY ROLES - PILOTS
            {
                'code': 'N-PIL-F',
                'title': 'Fighter Pilot',
                'branch': branches['UEEN'],
                'category': 'aviation',
                'description': 'Qualified to pilot light and medium fighters in combat operations',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 16,
                'ait_location': 'Port Olisar Flight Academy',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Trainee Pilot',
                    '20': 'Qualified Pilot',
                    '30': 'Senior Pilot',
                    '40': 'Master Pilot'
                }
            },
            {
                'code': 'N-PIL-B',
                'title': 'Bomber Pilot',
                'branch': branches['UEEN'],
                'category': 'aviation',
                'description': 'Specialized in heavy bomber and torpedo operations',
                'min_asvab_score': 100,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 20,
                'ait_location': 'Port Olisar Flight Academy',
                'is_entry_level': False,
                'skill_levels': {
                    '10': 'Bomber Trainee',
                    '20': 'Qualified Bomber Pilot',
                    '30': 'Senior Bomber Pilot',
                    '40': 'Master Bomber Pilot'
                }
            },
            {
                'code': 'N-PIL-T',
                'title': 'Transport Pilot',
                'branch': branches['UEEN'],
                'category': 'aviation',
                'description': 'Qualified to pilot dropships and transport vessels',
                'min_asvab_score': 90,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 12,
                'ait_location': 'Port Olisar Flight Academy',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Transport Trainee',
                    '20': 'Qualified Transport Pilot',
                    '30': 'Senior Transport Pilot',
                    '40': 'Master Transport Pilot'
                }
            },
            {
                'code': 'N-PIL-H',
                'title': 'Heavy Fighter Pilot',
                'branch': branches['UEEN'],
                'category': 'aviation',
                'description': 'Specialized in heavy fighters like Vanguard and Hurricane',
                'min_asvab_score': 98,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 18,
                'ait_location': 'Terra Naval Academy',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': 'N-PIL-I',
                'title': 'Interceptor Pilot',
                'branch': branches['UEEN'],
                'category': 'aviation',
                'description': 'High-speed intercept and space superiority specialist',
                'min_asvab_score': 100,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Ellis Racing Academy',
                'is_entry_level': False,
                'skill_levels': {}
            },

            # NAVY ROLES - CAPITAL SHIP OPERATIONS
            {
                'code': 'N-CMD',
                'title': 'Capital Ship Commander',
                'branch': branches['UEEN'],
                'category': 'command',
                'description': 'Qualified to command capital class vessels',
                'min_asvab_score': 110,
                'security_clearance_required': 'top_secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 52,
                'ait_location': 'Terra Naval Command School',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': 'N-NAV',
                'title': 'Navigation Officer',
                'branch': branches['UEEN'],
                'category': 'naval_operations',
                'description': 'Quantum jump calculations and stellar navigation',
                'min_asvab_score': 105,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 16,
                'ait_location': 'Terra Naval Academy',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'N-WPN',
                'title': 'Weapons Systems Officer',
                'branch': branches['UEEN'],
                'category': 'combat_systems',
                'description': 'Ship weapon systems operation and targeting',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 14,
                'ait_location': 'Hurston Weapons School',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'N-TUR',
                'title': 'Turret Gunner',
                'branch': branches['UEEN'],
                'category': 'combat_systems',
                'description': 'Operates manned turrets on capital ships',
                'min_asvab_score': 88,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 8,
                'ait_location': 'Hurston Weapons School',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Gunner',
                    '20': 'Qualified Gunner',
                    '30': 'Expert Gunner',
                    '40': 'Master Gunner'
                }
            },
            {
                'code': 'N-ENG',
                'title': 'Ship Engineer',
                'branch': branches['UEEN'],
                'category': 'engineering',
                'description': 'Maintains and repairs ship systems and components',
                'min_asvab_score': 100,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 20,
                'ait_location': 'ArcCorp Engineering Institute',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Engineering Apprentice',
                    '20': 'Systems Engineer',
                    '30': 'Senior Engineer',
                    '40': 'Master Engineer'
                }
            },
            {
                'code': 'N-SHD',
                'title': 'Shield Operator',
                'branch': branches['UEEN'],
                'category': 'combat_systems',
                'description': 'Manages ship shield systems and power distribution',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 10,
                'ait_location': 'Crusader Defense Academy',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'N-SEN',
                'title': 'Sensor Operator',
                'branch': branches['UEEN'],
                'category': 'naval_operations',
                'description': 'Operates scanning and detection systems',
                'min_asvab_score': 98,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 12,
                'ait_location': 'MicroTech Technical Institute',
                'is_entry_level': True,
                'skill_levels': {}
            },

            # MARINE ROLES
            {
                'code': 'M-AST',
                'title': 'Assault Specialist',
                'branch': branches['UEEM'],
                'category': 'combat_arms',
                'description': 'Ship boarding and station assault operations',
                'min_asvab_score': 87,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 16,
                'ait_location': 'Kilian Marine Training Center',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Marine',
                    '20': 'Assault Team Member',
                    '30': 'Assault Team Leader',
                    '40': 'Assault Squad Leader'
                }
            },
            {
                'code': 'M-BRC',
                'title': 'Breacher',
                'branch': branches['UEEM'],
                'category': 'combat_arms',
                'description': 'Specialized in forced entry and demolitions',
                'min_asvab_score': 90,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 14,
                'ait_location': 'Kilian Marine Training Center',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': 'M-SNP',
                'title': 'Marksman',
                'branch': branches['UEEM'],
                'category': 'combat_arms',
                'description': 'Precision shooting in zero-G environments',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 18,
                'ait_location': 'Vega Marksmanship School',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': 'M-ZGS',
                'title': 'Zero-G Specialist',
                'branch': branches['UEEM'],
                'category': 'combat_arms',
                'description': 'Expert in EVA combat and operations',
                'min_asvab_score': 92,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 20,
                'ait_location': 'Port Olisar Zero-G Training',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': 'M-HWS',
                'title': 'Heavy Weapons Specialist',
                'branch': branches['UEEM'],
                'category': 'combat_arms',
                'description': 'Operates railguns, rocket launchers, and heavy weapons',
                'min_asvab_score': 88,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 12,
                'ait_location': 'Hurston Heavy Weapons Range',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'M-MED',
                'title': 'Combat Medic',
                'branch': branches['UEEM'],
                'category': 'medical',
                'description': 'Emergency medical care in combat zones',
                'min_asvab_score': 101,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Hope Medical Station',
                'is_entry_level': True,
                'skill_levels': {}
            },

            # ARMY ROLES - GROUND OPERATIONS
            {
                'code': 'A-TNK',
                'title': 'Tank Commander',
                'branch': branches['UEEA'],
                'category': 'armor',
                'description': 'Commands Nova or Ballista tank operations',
                'min_asvab_score': 90,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Aberdeen Armor School',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'A-RCN',
                'title': 'Ground Reconnaissance',
                'branch': branches['UEEA'],
                'category': 'combat_arms',
                'description': 'Planetary reconnaissance and scouting',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 20,
                'ait_location': 'Daymar Recon School',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'A-ART',
                'title': 'Artillery Specialist',
                'branch': branches['UEEA'],
                'category': 'combat_arms',
                'description': 'Operates ground-based artillery and AA systems',
                'min_asvab_score': 93,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 12,
                'ait_location': 'Hurston Artillery Range',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'A-VOP',
                'title': 'Vehicle Operator',
                'branch': branches['UEEA'],
                'category': 'armor',
                'description': 'Operates Cyclone, Ursa, and other ground vehicles',
                'min_asvab_score': 85,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 8,
                'ait_location': 'Hurston Vehicle Course',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'A-INF',
                'title': 'Infantry Specialist',
                'branch': branches['UEEA'],
                'category': 'combat_arms',
                'description': 'Ground combat operations specialist',
                'min_asvab_score': 87,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 14,
                'ait_location': 'Kilian Infantry School',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Infantry',
                    '20': 'Infantry Team Leader',
                    '30': 'Infantry Squad Leader',
                    '40': 'Infantry Platoon Sergeant'
                }
            },

            # SUPPORT ROLES - ALL BRANCHES
            {
                'code': 'S-LOG',
                'title': 'Logistics Specialist',
                'branch': branches['UEEN'],
                'category': 'logistics',
                'description': 'Cargo operations and supply chain management',
                'min_asvab_score': 90,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 10,
                'ait_location': 'Area 18 Logistics Center',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-MIN',
                'title': 'Mining Specialist',
                'branch': branches['UEEN'],
                'category': 'industrial',
                'description': 'Resource extraction and refinery operations',
                'min_asvab_score': 85,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 8,
                'ait_location': 'Prospector Training Facility',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-SAL',
                'title': 'Salvage Specialist',
                'branch': branches['UEEN'],
                'category': 'industrial',
                'description': 'Ship salvage and component recovery operations',
                'min_asvab_score': 88,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 10,
                'ait_location': 'Reclaimer Training Center',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-INT',
                'title': 'Intelligence Analyst',
                'branch': branches['UEEN'],
                'category': 'intelligence',
                'description': 'Signal intelligence and threat assessment',
                'min_asvab_score': 105,
                'security_clearance_required': 'top_secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 20,
                'ait_location': 'Terra Intelligence School',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-COM',
                'title': 'Communications Specialist',
                'branch': branches['UEEN'],
                'category': 'signal',
                'description': 'Quantum communications and data systems',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 16,
                'ait_location': 'MicroTech Comm School',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-SEC',
                'title': 'Security Forces',
                'branch': branches['UEEM'],
                'category': 'security',
                'description': 'Station and outpost security operations',
                'min_asvab_score': 91,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 12,
                'ait_location': 'Lorville Security Academy',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-SAR',
                'title': 'Search and Rescue',
                'branch': branches['UEEN'],
                'category': 'medical',
                'description': 'Emergency rescue operations in space',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 20,
                'ait_location': 'Crusader SAR Academy',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-MED',
                'title': 'Medical Officer',
                'branch': branches['UEEN'],
                'category': 'medical',
                'description': 'Advanced medical care and surgery',
                'min_asvab_score': 105,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'light',
                'ait_weeks': 36,
                'ait_location': 'Hope Medical Academy',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': 'S-CRG',
                'title': 'Cargo Specialist',
                'branch': branches['UEEN'],
                'category': 'logistics',
                'description': 'Cargo loading, securing, and transport',
                'min_asvab_score': 85,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 6,
                'ait_location': 'Hull-C Training Facility',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-REP',
                'title': 'Repair Specialist',
                'branch': branches['UEEN'],
                'category': 'engineering',
                'description': 'Field repairs and maintenance operations',
                'min_asvab_score': 95,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 14,
                'ait_location': 'Crucible Repair School',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-FUE',
                'title': 'Refueling Specialist',
                'branch': branches['UEEN'],
                'category': 'logistics',
                'description': 'In-flight refueling and fuel management',
                'min_asvab_score': 88,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 8,
                'ait_location': 'Starfarer Training Center',
                'is_entry_level': True,
                'skill_levels': {}
            },
            {
                'code': 'S-EXP',
                'title': 'Exploration Specialist',
                'branch': branches['UEEN'],
                'category': 'naval_operations',
                'description': 'Deep space exploration and pathfinding',
                'min_asvab_score': 100,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 24,
                'ait_location': 'Carrack Exploration Academy',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': 'S-EWS',
                'title': 'Electronic Warfare Specialist',
                'branch': branches['UEEN'],
                'category': 'intelligence',
                'description': 'Electronic countermeasures and cyber warfare',
                'min_asvab_score': 108,
                'security_clearance_required': 'top_secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 26,
                'ait_location': 'Sentinel EW School',
                'is_entry_level': False,
                'skill_levels': {}
            },
        ]