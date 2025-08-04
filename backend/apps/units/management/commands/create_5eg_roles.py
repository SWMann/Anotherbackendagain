# backend/apps/units/management/commands/create_5eg_roles.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.units.models import Role, Branch, Rank


class Command(BaseCommand):
    help = 'Creates all roles for the 5th Expeditionary Group'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Get UEE branch
            try:
                uee_branch = Branch.objects.get(abbreviation='UEEN')
            except Branch.DoesNotExist:
                self.stdout.write(self.style.ERROR('UEE branch not found. Please create it first.'))
                return

            # Get ranks for min/max requirements
            ranks = {r.abbreviation: r for r in Rank.objects.filter(branch=uee_branch)}

            # Track statistics
            created_count = 0
            updated_count = 0
            skipped_count = 0

            # Define all roles
            roles_data = self.get_roles_data(uee_branch, ranks)

            # Create or update roles
            for role_info in roles_data:
                try:
                    # Extract M2M fields
                    allowed_branches = role_info.pop('allowed_branches', [])

                    # Create or update role
                    role, created = Role.objects.update_or_create(
                        name=role_info['name'],
                        defaults=role_info
                    )

                    # Set allowed branches
                    if allowed_branches:
                        role.allowed_branches.set(allowed_branches)
                    else:
                        role.allowed_branches.set([uee_branch])

                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Created role: {role.name}'))
                    else:
                        updated_count += 1
                        self.stdout.write(f'Updated role: {role.name}')

                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.ERROR(f'Error with role {role_info["name"]}: {str(e)}'))

            # Summary
            self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
            self.stdout.write(self.style.SUCCESS(f'Created: {created_count} roles'))
            self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count} roles'))
            if skipped_count > 0:
                self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} roles'))

            # Category summary
            categories = {}
            for role in Role.objects.filter(allowed_branches=uee_branch):
                cat = role.category
                categories[cat] = categories.get(cat, 0) + 1

            self.stdout.write(self.style.SUCCESS(f'\nRoles by Category:'))
            for cat, count in sorted(categories.items()):
                self.stdout.write(f'  {cat}: {count}')

    def get_roles_data(self, uee_branch, ranks):
        """Returns the complete role data for 5th Expeditionary Group"""
        return [
            # COMMAND POSITIONS
            {
                'name': 'Captain',
                'abbreviation': 'CAPT',
                'category': 'command',
                'description': 'Commands naval vessels of corvette classification or larger. Provides strategic leadership and direction to the entire crew.',
                'is_command_role': True,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LCDR'),
                'max_rank': ranks.get('CAPT'),
                'typical_rank': ranks.get('CDR'),
                'allowed_unit_types': ['vessel', 'squadron'],
                'min_time_in_service': 2190,  # 6 years
                'min_time_in_grade': 365,
                'min_operations_count': 20,
                'responsibilities': 'Overall ship command, strategic decision-making, crew leadership, mission planning, liaison with fleet command',
                'authorities': 'Full command authority over vessel and crew, tactical decision authority, disciplinary authority',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'Executive Officer',
                'abbreviation': 'XO',
                'category': 'command',
                'description': 'Second in command on vessels above corvette classification. Manages daily ship administration and stands ready to assume command.',
                'is_command_role': True,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LT'),
                'max_rank': ranks.get('CDR'),
                'typical_rank': ranks.get('LCDR'),
                'allowed_unit_types': ['vessel', 'squadron'],
                'min_time_in_service': 1460,  # 4 years
                'min_time_in_grade': 365,
                'min_operations_count': 15,
                'responsibilities': 'Daily ship operations, crew administration, personnel management, command preparation, maintaining operational awareness of all ship systems',
                'authorities': 'Acting command authority, administrative authority, personnel management authority',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 2
            },

            # AVIATION COMMAND
            {
                'name': 'Squadron Leader',
                'abbreviation': 'SQL',
                'category': 'aviation',
                'description': 'Commands 5-6 wings of aircraft while maintaining flight status. Last command position to actively fly.',
                'is_command_role': True,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LCDR'),
                'max_rank': ranks.get('CDR'),
                'typical_rank': ranks.get('LCDR'),
                'allowed_unit_types': ['squadron', 'air_wing'],
                'min_time_in_service': 2190,
                'min_time_in_grade': 730,
                'min_operations_count': 50,
                'responsibilities': 'Squadron operations, multi-wing coordination, tactical planning, battlefield effects assessment',
                'authorities': 'Squadron command authority, flight operations authority, tactical decision authority',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 10
            },
            {
                'name': 'Squadron Executive Officer',
                'abbreviation': 'SXO',
                'category': 'aviation',
                'description': 'Second in command of aviation squadron, maintains flight status. Last executive position to actively fly.',
                'is_command_role': True,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LT'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['squadron', 'air_wing'],
                'min_time_in_service': 1095,
                'min_time_in_grade': 365,
                'min_operations_count': 30,
                'responsibilities': 'Squadron administration, operational planning support, command preparation, personnel management',
                'authorities': 'Acting squadron command, administrative authority, flight operations coordination',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 11
            },
            {
                'name': 'Wing Leader',
                'abbreviation': 'WL',
                'category': 'aviation',
                'description': 'Commands a wing of 4 aircraft while maintaining flight status.',
                'is_command_role': True,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LT'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['flight', 'squadron'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 20,
                'responsibilities': 'Wing coordination, tactical leadership, target management, communication with higher command',
                'authorities': 'Wing command authority, tactical decision authority, flight operations control',
                'default_slots_per_unit': 4,
                'max_slots_per_unit': 6,
                'is_active': True,
                'sort_order': 12
            },

            # DEPARTMENT HEADS
            {
                'name': 'Engineering Officer',
                'abbreviation': 'ENG',
                'category': 'staff',
                'description': 'Department head responsible for all ship engineering systems. Requires intimate knowledge of specific vessel.',
                'is_command_role': False,
                'is_staff_role': True,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LTJG'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 10,
                'responsibilities': 'Engineering systems oversight, damage control, power management, component maintenance, operational readiness',
                'authorities': 'Engineering department authority, maintenance authorization, emergency response authority',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 20
            },
            {
                'name': 'Weapons Officer',
                'abbreviation': 'WEPS',
                'category': 'staff',
                'description': 'Coordinates all offensive and defensive weapons systems on frigates and larger vessels.',
                'is_command_role': False,
                'is_staff_role': True,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LTJG'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 10,
                'responsibilities': 'Weapons employment, gunnery section coordination, fire mission planning, ordnance management, tactical fire control',
                'authorities': 'Weapons release authority, fire control authority, ordnance management',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 21
            },
            {
                'name': 'Medical Officer',
                'abbreviation': 'MO',
                'category': 'medical',
                'description': 'Department head coordinating all medical staff aboard ship.',
                'is_command_role': False,
                'is_staff_role': True,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('LT'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['vessel', 'division', 'brigade'],
                'min_time_in_service': 1095,
                'min_time_in_grade': 365,
                'min_operations_count': 5,
                'responsibilities': 'Medical department coordination, med bay management, personnel assignment, capability assessment, advising command on medical readiness',
                'authorities': 'Medical treatment authority, medical evacuation authority, quarantine authority',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 22
            },
            {
                'name': 'Logistics Officer',
                'abbreviation': 'LOG',
                'category': 'logistics',
                'description': 'Bridge crew member coordinating all logistics operations.',
                'is_command_role': False,
                'is_staff_role': True,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('LTJG'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['vessel', 'squadron', 'division'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 10,
                'responsibilities': 'Cargo operations, resource management, rearmament coordination, supply chain management, first responder duties',
                'authorities': 'Logistics operations authority, resource allocation, emergency logistics',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 23
            },
            {
                'name': 'Aviation Officer',
                'abbreviation': 'AVO',
                'category': 'aviation',
                'description': 'Coordinates all aviation flights within the ship.',
                'is_command_role': False,
                'is_staff_role': True,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('LT'),
                'max_rank': ranks.get('CDR'),
                'typical_rank': ranks.get('LCDR'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 1460,
                'min_time_in_grade': 365,
                'min_operations_count': 30,
                'responsibilities': 'Flight coordination, launch/recovery scheduling, maintenance coordination with engineering, backup ATC duties',
                'authorities': 'Flight operations authority, deck operations control, maintenance priorities',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 1,
                'is_active': True,
                'sort_order': 24
            },

            # BRIDGE OPERATIONS
            {
                'name': 'Communications Officer',
                'abbreviation': 'COMMS',
                'category': 'communications',
                'description': 'Manages all internal and external communications.',
                'is_command_role': False,
                'is_staff_role': True,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('Ens'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LTJG'),
                'allowed_unit_types': ['vessel', 'squadron', 'division'],
                'min_time_in_service': 365,
                'min_time_in_grade': 90,
                'min_operations_count': 5,
                'responsibilities': 'Intra-ship coordination between sections, inter-unit communications, net control, establishing communication protocols',
                'authorities': 'Communications control, encryption authority, net management',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 2,
                'is_active': True,
                'sort_order': 30
            },
            {
                'name': 'Helmsman',
                'abbreviation': 'HELM',
                'category': 'specialist',
                'description': 'Primary pilot responsible for maneuvering the vessel.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('PO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 20,
                'responsibilities': 'Ship piloting, maneuvering in combat and navigation, docking procedures, emergency evasion',
                'authorities': 'Ship maneuvering control, emergency maneuver authority',
                'default_slots_per_unit': 3,
                'max_slots_per_unit': 4,
                'is_active': True,
                'sort_order': 31
            },
            {
                'name': 'Navigator',
                'abbreviation': 'NAV',
                'category': 'specialist',
                'description': 'Assists the helmsman as co-pilot, handles route planning and threat awareness.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('JPO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 365,
                'min_time_in_grade': 180,
                'min_operations_count': 10,
                'responsibilities': 'Route plotting, quantum jump calculations, threat spotting, landing assistance, providing extra situational awareness',
                'authorities': 'Navigation planning, sensor operations',
                'default_slots_per_unit': 3,
                'max_slots_per_unit': 4,
                'is_active': True,
                'sort_order': 32
            },
            {
                'name': 'Air Traffic Controller',
                'abbreviation': 'ATC',
                'category': 'specialist',
                'description': 'Manages flight deck operations and coordinates launch/recovery procedures.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('PO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 15,
                'responsibilities': 'Flight deck management, hangar door operations, launch/recovery communications, squadron coordination',
                'authorities': 'Flight deck control, launch/recovery authorization, emergency procedures',
                'default_slots_per_unit': 2,
                'max_slots_per_unit': 4,
                'is_active': True,
                'sort_order': 33
            },

            # AVIATION OPERATIONS
            {
                'name': 'Pilot (Fighter)',
                'abbreviation': 'PLT-F',
                'category': 'aviation',
                'description': 'Specialist in small to medium fighter aircraft operations and air-to-air combat.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('Ens'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LTJG'),
                'allowed_unit_types': ['squadron', 'flight'],
                'min_time_in_service': 180,
                'min_time_in_grade': 90,
                'min_operations_count': 10,
                'responsibilities': 'Fighter operations, air superiority missions, fleet defense, escort duties',
                'authorities': 'Aircraft operation, weapons employment, emergency procedures',
                'default_slots_per_unit': 8,
                'max_slots_per_unit': 24,
                'is_active': True,
                'sort_order': 40
            },
            {
                'name': 'Pilot (Interceptor)',
                'abbreviation': 'PLT-I',
                'category': 'aviation',
                'description': 'Specialized in high-speed interception tactics and pursuit operations.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('LTJG'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['squadron', 'flight'],
                'min_time_in_service': 365,
                'min_time_in_grade': 180,
                'min_operations_count': 20,
                'responsibilities': 'High-speed interception, pursuit operations, fleeing craft neutralization, rapid response',
                'authorities': 'Pursuit authorization, high-speed engagement, emergency response',
                'default_slots_per_unit': 4,
                'max_slots_per_unit': 12,
                'is_active': True,
                'sort_order': 41
            },
            {
                'name': 'Pilot (Bomber)',
                'abbreviation': 'PLT-B',
                'category': 'aviation',
                'description': 'Specialist in bomber aircraft for ground attack and anti-capital ship operations.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('LTJG'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['squadron', 'flight'],
                'min_time_in_service': 365,
                'min_time_in_grade': 180,
                'min_operations_count': 15,
                'responsibilities': 'Strategic bombing, torpedo runs, ground support, coordinated squadron attacks',
                'authorities': 'Heavy ordnance employment, coordinated attack authorization',
                'default_slots_per_unit': 4,
                'max_slots_per_unit': 16,
                'is_active': True,
                'sort_order': 42
            },
            {
                'name': 'Pilot (Recon)',
                'abbreviation': 'PLT-R',
                'category': 'aviation',
                'description': 'Stealth and reconnaissance specialist operating behind enemy lines.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('LTJG'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['squadron', 'flight'],
                'min_time_in_service': 365,
                'min_time_in_grade': 180,
                'min_operations_count': 15,
                'responsibilities': 'Intelligence gathering, stealth operations, long-range reconnaissance, isolated operations',
                'authorities': 'Independent operation, intelligence gathering, emergency extraction',
                'default_slots_per_unit': 2,
                'max_slots_per_unit': 8,
                'is_active': True,
                'sort_order': 43
            },
            {
                'name': 'Pilot (Dropship)',
                'abbreviation': 'PLT-D',
                'category': 'aviation',
                'description': 'Specialist in troop transport and combat insertion operations.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('Ens'),
                'max_rank': ranks.get('LCDR'),
                'typical_rank': ranks.get('LTJG'),
                'allowed_unit_types': ['squadron', 'flight'],
                'min_time_in_service': 180,
                'min_time_in_grade': 90,
                'min_operations_count': 10,
                'responsibilities': 'Troop transport, hot LZ insertions, ground coordination, passenger safety',
                'authorities': 'Transport operations, emergency extraction, ground force coordination',
                'default_slots_per_unit': 4,
                'max_slots_per_unit': 12,
                'is_active': True,
                'sort_order': 44
            },
            {
                'name': 'Pilot (Transport)',
                'abbreviation': 'PLT-T',
                'category': 'aviation',
                'description': 'Cargo transport specialist for logistics operations.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('Ens'),
                'max_rank': ranks.get('LT'),
                'typical_rank': ranks.get('LTJG'),
                'allowed_unit_types': ['squadron', 'flight'],
                'min_time_in_service': 180,
                'min_time_in_grade': 90,
                'min_operations_count': 5,
                'responsibilities': 'Cargo transport, long-range logistics, route planning, cargo handling',
                'authorities': 'Cargo operations, route selection, emergency procedures',
                'default_slots_per_unit': 2,
                'max_slots_per_unit': 8,
                'is_active': True,
                'sort_order': 45
            },

            # MEDICAL DEPARTMENT
            {
                'name': 'Doctor',
                'abbreviation': 'DOC',
                'category': 'medical',
                'description': 'Senior medical personnel with extensive training.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('LTJG'),
                'max_rank': ranks.get('LT'),
                'typical_rank': ranks.get('LT'),
                'allowed_unit_types': ['vessel', 'division', 'brigade'],
                'min_time_in_service': 730,
                'min_time_in_grade': 365,
                'min_operations_count': 5,
                'responsibilities': 'Medical supervision, advanced medical procedures, department coordination in absence of MO, combat medical response',
                'authorities': 'Medical treatment, surgical procedures, medical evacuation recommendation',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 2,
                'is_active': True,
                'sort_order': 50
            },
            {
                'name': 'Medic',
                'abbreviation': 'MED',
                'category': 'medical',
                'description': 'General medical personnel responsible for med bay operations and first response.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('JPO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel', 'company', 'platoon'],
                'min_time_in_service': 180,
                'min_time_in_grade': 90,
                'min_operations_count': 5,
                'responsibilities': 'Med bay operations, patient care, emergency response, combat medic duties when required',
                'authorities': 'Basic medical treatment, first aid, stabilization procedures',
                'default_slots_per_unit': 2,
                'max_slots_per_unit': 6,
                'is_active': True,
                'sort_order': 51
            },
            {
                'name': 'Paramedic/Pararescue',
                'abbreviation': 'PJ',
                'category': 'medical',
                'description': 'Specialized medics trained for high-risk rescue operations and advanced trauma care.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('PO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel', 'squadron', 'company'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 10,
                'responsibilities': 'High-risk medical extraction, advanced trauma care, combat rescue operations, specialized equipment operation',
                'authorities': 'Emergency extraction, advanced trauma procedures, field surgery',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 3,
                'is_active': True,
                'sort_order': 52
            },

            # GUNNERY DEPARTMENT
            {
                'name': 'Gunnery Chief',
                'abbreviation': 'GC',
                'category': 'nco',
                'description': 'Senior warrant officer responsible for all turret operations aboard ship.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': True,
                'is_specialist_role': False,
                'min_rank': ranks.get('CPO'),
                'max_rank': ranks.get('MCPO'),
                'typical_rank': ranks.get('CPO'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 1460,
                'min_time_in_grade': 365,
                'min_operations_count': 20,
                'responsibilities': 'All turret operations, gunnery training, personnel conduct, weapons employment strategy',
                'authorities': 'Gunnery operations control, training authority, section management',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 2,
                'is_active': True,
                'sort_order': 60
            },
            {
                'name': 'Gunnery Lead',
                'abbreviation': 'GL',
                'category': 'nco',
                'description': 'Coordinates 4-5 turrets while maintaining turret operation duties.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': True,
                'is_specialist_role': False,
                'min_rank': ranks.get('PO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 15,
                'responsibilities': 'Multi-turret coordination, team leadership, communication with gunnery chief/weapons officer',
                'authorities': 'Section command, fire coordination, team management',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 3,
                'is_active': True,
                'sort_order': 61
            },
            {
                'name': 'Gunner',
                'abbreviation': 'GNR',
                'category': 'specialist',
                'description': 'Operates ship weapon systems including turrets and torpedoes.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('Strm'),
                'max_rank': ranks.get('JPO'),
                'typical_rank': ranks.get('LStrm'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 90,
                'min_time_in_grade': 30,
                'min_operations_count': 5,
                'responsibilities': 'Turret operation, weapons maintenance, target engagement, fire safety',
                'authorities': 'Weapons operation, maintenance procedures',
                'default_slots_per_unit': 4,
                'max_slots_per_unit': 12,
                'is_active': True,
                'sort_order': 62
            },

            # ENGINEERING DEPARTMENT
            {
                'name': 'Engineering Chief',
                'abbreviation': 'EC',
                'category': 'nco',
                'description': 'Senior engineering personnel responsible for all engineering operations below officer level.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': True,
                'is_specialist_role': False,
                'min_rank': ranks.get('CPO'),
                'max_rank': ranks.get('MCPO'),
                'typical_rank': ranks.get('CPO'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 1460,
                'min_time_in_grade': 365,
                'min_operations_count': 20,
                'responsibilities': 'Engineering department leadership, complete technical knowledge, ship modification recommendations, team training',
                'authorities': 'Engineering operations control, maintenance authorization, training authority',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 2,
                'is_active': True,
                'sort_order': 70
            },
            {
                'name': 'Engineering Lead',
                'abbreviation': 'EL',
                'category': 'nco',
                'description': 'Team leader for engineering crews, coordinates repair teams.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': True,
                'is_specialist_role': False,
                'min_rank': ranks.get('PO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 15,
                'responsibilities': 'Team coordination, task prioritization, cross-crew communication, technical supervision',
                'authorities': 'Team leadership, work assignment, quality control',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 4,
                'is_active': True,
                'sort_order': 71
            },
            {
                'name': 'Engineer',
                'abbreviation': 'ENG',
                'category': 'specialist',
                'description': 'Entry-level engineering position learning ship-specific systems.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('Strm'),
                'max_rank': ranks.get('JPO'),
                'typical_rank': ranks.get('LStrm'),
                'allowed_unit_types': ['vessel'],
                'min_time_in_service': 90,
                'min_time_in_grade': 30,
                'min_operations_count': 5,
                'responsibilities': 'Ship maintenance, fire suppression, relay terminal repairs, general engineering support',
                'authorities': 'Basic maintenance, emergency repairs',
                'default_slots_per_unit': 4,
                'max_slots_per_unit': 12,
                'is_active': True,
                'sort_order': 72
            },

            # LOGISTICS DEPARTMENT
            {
                'name': 'Logistics Lead',
                'abbreviation': 'LL',
                'category': 'nco',
                'description': 'Team leader for logistics operations, coordinates logistics teams.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': True,
                'is_specialist_role': False,
                'min_rank': ranks.get('PO'),
                'max_rank': ranks.get('CPO'),
                'typical_rank': ranks.get('PO'),
                'allowed_unit_types': ['vessel', 'division'],
                'min_time_in_service': 730,
                'min_time_in_grade': 180,
                'min_operations_count': 10,
                'responsibilities': 'Team coordination, logistics planning, department communication, operational efficiency',
                'authorities': 'Team leadership, resource allocation, priority management',
                'default_slots_per_unit': 1,
                'max_slots_per_unit': 2,
                'is_active': True,
                'sort_order': 80
            },
            {
                'name': 'Logistics Operator',
                'abbreviation': 'LOG',
                'category': 'specialist',
                'description': 'General logistics crew operating tractor beams, repair tools, and cargo movement systems.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': True,
                'min_rank': ranks.get('Strm'),
                'max_rank': ranks.get('JPO'),
                'typical_rank': ranks.get('AStrm'),
                'allowed_unit_types': ['vessel', 'division'],
                'min_time_in_service': 90,
                'min_time_in_grade': 30,
                'min_operations_count': 5,
                'responsibilities': 'Cargo handling, flight deck operations, refueling/rearming support, ground component coordination',
                'authorities': 'Cargo operations, equipment operation',
                'default_slots_per_unit': 2,
                'max_slots_per_unit': 8,
                'is_active': True,
                'sort_order': 81
            },

            # GENERAL CREW
            {
                'name': 'Crewman',
                'abbreviation': 'CM',
                'category': 'trooper',
                'description': 'Entry-level generalist position with massive flexibility.',
                'is_command_role': False,
                'is_staff_role': False,
                'is_nco_role': False,
                'is_specialist_role': False,
                'min_rank': ranks.get('NRct'),
                'max_rank': ranks.get('JPO'),
                'typical_rank': ranks.get('Strm'),
                'allowed_unit_types': ['vessel', 'squadron', 'company', 'platoon'],
                'min_time_in_service': 0,
                'min_time_in_grade': 0,
                'min_operations_count': 0,
                'responsibilities': 'General assistance, cross-department support, learning ship operations, flexible assignment',
                'authorities': 'Basic operations as directed',
                'default_slots_per_unit': 0,  # Ad-hoc assignment
                'max_slots_per_unit': 999,  # Unlimited
                'is_active': True,
                'sort_order': 90
            }
        ]