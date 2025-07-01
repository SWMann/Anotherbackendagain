# backend/apps/units/management/commands/create_mos_data.py

from django.core.management.base import BaseCommand
from apps.units.models import MOS, Branch


class Command(BaseCommand):
    help = 'Creates MOS data for US Army units'

    def handle(self, *args, **options):
        # Define MOS data
        mos_data = [
            # OFFICER MOS (Branch Qualified)
            {
                'code': '11A',
                'title': 'Infantry Officer',
                'category': 'combat_arms',
                'description': 'Leads infantry units in combat operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 17,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '12A',
                'title': 'Engineer Officer',
                'category': 'combat_arms',
                'description': 'Leads engineer units in combat and construction operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 20,
                'ait_location': 'Fort Leonard Wood, MO',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '13A',
                'title': 'Field Artillery Officer',
                'category': 'combat_arms',
                'description': 'Leads field artillery units in fire support operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 18,
                'ait_location': 'Fort Sill, OK',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '14A',
                'title': 'Air Defense Artillery Officer',
                'category': 'combat_support',
                'description': 'Leads air defense units protecting forces from aerial threats',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 18,
                'ait_location': 'Fort Sill, OK',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '15A',
                'title': 'Aviation Officer',
                'category': 'aviation',
                'description': 'Commands aviation units and serves as rated aviator',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 52,
                'ait_location': 'Fort Rucker, AL',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '19A',
                'title': 'Armor Officer',
                'category': 'combat_arms',
                'description': 'Leads armor and cavalry units in mobile combat operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '25A',
                'title': 'Signal Officer',
                'category': 'signal',
                'description': 'Leads signal units in communications and network operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 24,
                'ait_location': 'Fort Gordon, GA',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '31A',
                'title': 'Military Police Officer',
                'category': 'combat_support',
                'description': 'Leads military police units in law enforcement and security operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 16,
                'ait_location': 'Fort Leonard Wood, MO',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '35A',
                'title': 'Military Intelligence Officer',
                'category': 'intelligence',
                'description': 'Leads intelligence collection and analysis operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'top_secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 16,
                'ait_location': 'Fort Huachuca, AZ',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '60A',
                'title': 'Medical Corps Officer',
                'category': 'medical',
                'description': 'Physician providing medical care and leading medical units',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 0,
                'ait_location': 'Direct Commission',
                'is_entry_level': False,
                'skill_levels': {}
            },
            {
                'code': '90A',
                'title': 'Logistics Officer',
                'category': 'logistics',
                'description': 'Leads logistics units in sustainment operations',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 16,
                'ait_location': 'Fort Lee, VA',
                'is_entry_level': False,
                'skill_levels': {}
            },

            # INFANTRY ENLISTED
            {
                'code': '11B',
                'title': 'Infantryman',
                'category': 'combat_arms',
                'description': 'Serves as member of infantry unit, performs combat operations',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 14,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Infantryman',
                    '20': 'Infantry Team Leader',
                    '30': 'Infantry Squad Leader',
                    '40': 'Infantry Platoon Sergeant'
                }
            },
            {
                'code': '11C',
                'title': 'Indirect Fire Infantryman',
                'category': 'combat_arms',
                'description': 'Operates mortars in support of infantry operations',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 14,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Mortarman',
                    '20': 'Mortar Squad Leader',
                    '30': 'Mortar Section Sergeant',
                    '40': 'Mortar Platoon Sergeant'
                }
            },

            # ARMOR ENLISTED
            {
                'code': '19D',
                'title': 'Cavalry Scout',
                'category': 'combat_arms',
                'description': 'Performs reconnaissance and security missions',
                'min_asvab_score': 87,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Scout',
                    '20': 'Scout Team Leader',
                    '30': 'Scout Squad Leader',
                    '40': 'Scout Platoon Sergeant'
                }
            },
            {
                'code': '19K',
                'title': 'M1 Armor Crewman',
                'category': 'combat_arms',
                'description': 'Operates M1 Abrams Main Battle Tank',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 15,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Tank Driver/Loader',
                    '20': 'Tank Gunner',
                    '30': 'Tank Commander',
                    '40': 'Tank Platoon Sergeant'
                }
            },

            # ADDITIONAL ARMOR MOS
            {
                'code': '19C',
                'title': 'M2/M3 Bradley Fighting Vehicle Crewman',
                'category': 'combat_arms',
                'description': 'Operates Bradley Fighting Vehicles in mechanized infantry operations',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 15,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Bradley Driver',
                    '20': 'Bradley Gunner',
                    '30': 'Bradley Commander',
                    '40': 'Mechanized Platoon Sergeant'
                }
            },

            # FIELD ARTILLERY
            {
                'code': '13B',
                'title': 'Cannon Crewmember',
                'category': 'combat_arms',
                'description': 'Operates howitzers and artillery pieces',
                'min_asvab_score': 93,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 6,
                'ait_location': 'Fort Sill, OK',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Cannoneer',
                    '20': 'Gunner',
                    '30': 'Section Chief',
                    '40': 'Platoon Sergeant'
                }
            },
            {
                'code': '13F',
                'title': 'Fire Support Specialist',
                'category': 'combat_arms',
                'description': 'Provides targeting data for artillery and close air support',
                'min_asvab_score': 96,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 13,
                'ait_location': 'Fort Sill, OK',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Forward Observer',
                    '20': 'Fire Support Sergeant',
                    '30': 'Fire Support NCO',
                    '40': 'Master Fire Support NCO'
                }
            },

            # COMBAT ENGINEERS
            {
                'code': '12B',
                'title': 'Combat Engineer',
                'category': 'combat_arms',
                'description': 'Performs combat engineering and demolition operations',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'very_heavy',
                'ait_weeks': 14,
                'ait_location': 'Fort Leonard Wood, MO',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Basic Combat Engineer',
                    '20': 'Combat Engineer Team Leader',
                    '30': 'Combat Engineer Squad Leader',
                    '40': 'Combat Engineer Platoon Sergeant'
                }
            },

            # AVIATION - EXPANDED
            {
                'code': '15B',
                'title': 'Aircraft Powerplant Repairer',
                'category': 'aviation',
                'description': 'Maintains and repairs aircraft turbine engines',
                'min_asvab_score': 104,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 15,
                'ait_location': 'Fort Eustis, VA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Powerplant Mechanic',
                    '20': 'Senior Powerplant Mechanic',
                    '30': 'Powerplant NCO',
                    '40': 'Maintenance Supervisor'
                }
            },
            {
                'code': '15R',
                'title': 'Aircraft Repairer',
                'category': 'aviation',
                'description': 'Maintains and repairs Army rotary wing aircraft',
                'min_asvab_score': 104,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 16,
                'ait_location': 'Fort Eustis, VA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Aircraft Mechanic',
                    '20': 'Senior Aircraft Mechanic',
                    '30': 'Aircraft Maintenance NCO',
                    '40': 'Aircraft Maintenance Supervisor'
                }
            },
            {
                'code': '15W',
                'title': 'Unmanned Aircraft Systems Operator',
                'category': 'aviation',
                'description': 'Operates unmanned aircraft for reconnaissance',
                'min_asvab_score': 102,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 23,
                'ait_location': 'Fort Huachuca, AZ',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'UAS Operator',
                    '20': 'Senior UAS Operator',
                    '30': 'UAS Mission Coordinator',
                    '40': 'UAS Platoon Sergeant'
                }
            },

            # AVIATION WARRANT OFFICERS
            {
                'code': '153A',
                'title': 'Rotary Wing Aviator',
                'category': 'aviation',
                'description': 'Pilots Army rotary wing aircraft',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 52,
                'ait_location': 'Fort Rucker, AL',
                'is_entry_level': False,
                'requires_reclassification': True,
                'skill_levels': {}
            },
            {
                'code': '153D',
                'title': 'Apache Pilot',
                'category': 'aviation',
                'description': 'Pilots AH-64 Apache attack helicopters',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 60,
                'ait_location': 'Fort Rucker, AL',
                'is_entry_level': False,
                'requires_reclassification': True,
                'skill_levels': {}
            },
            {
                'code': '153M',
                'title': 'UH-60 Pilot',
                'category': 'aviation',
                'description': 'Pilots UH-60 Black Hawk helicopters',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 52,
                'ait_location': 'Fort Rucker, AL',
                'is_entry_level': False,
                'requires_reclassification': True,
                'skill_levels': {}
            },
            {
                'code': '153E',
                'title': 'OH-58 Kiowa Pilot',
                'category': 'aviation',
                'description': 'Pilots OH-58 Kiowa scout helicopters',
                'min_asvab_score': 110,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 52,
                'ait_location': 'Fort Rucker, AL',
                'is_entry_level': False,
                'requires_reclassification': True,
                'skill_levels': {}
            },

            # SIMPLIFIED COMBAT SUPPORT
            {
                'code': '31B',
                'title': 'Military Police',
                'category': 'combat_support',
                'description': 'Provides law enforcement and security',
                'min_asvab_score': 91,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 20,
                'ait_location': 'Fort Leonard Wood, MO',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Military Police',
                    '20': 'Military Police Team Leader',
                    '30': 'Military Police Squad Leader',
                    '40': 'Military Police Platoon Sergeant'
                }
            },
            {
                'code': '35F',
                'title': 'Intelligence Analyst',
                'category': 'intelligence',
                'description': 'Analyzes intelligence information',
                'min_asvab_score': 101,
                'security_clearance_required': 'top_secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 16,
                'ait_location': 'Fort Huachuca, AZ',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Intelligence Analyst',
                    '20': 'Senior Intelligence Analyst',
                    '30': 'Intelligence Sergeant',
                    '40': 'Intelligence Operations Sergeant'
                }
            },
            {
                'code': '25B',
                'title': 'Information Technology Specialist',
                'category': 'signal',
                'description': 'Manages information systems and networks',
                'min_asvab_score': 95,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 20,
                'ait_location': 'Fort Gordon, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'IT Specialist',
                    '20': 'Senior IT Specialist',
                    '30': 'IT Sergeant',
                    '40': 'IT Operations Sergeant'
                }
            },
            {
                'code': '25U',
                'title': 'Signal Support Systems Specialist',
                'category': 'signal',
                'description': 'Maintains communications equipment',
                'min_asvab_score': 96,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 16,
                'ait_location': 'Fort Gordon, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Signal Support Specialist',
                    '20': 'Senior Signal Support Specialist',
                    '30': 'Signal Support NCO',
                    '40': 'Signal Support Chief'
                }
            },

            # MEDICAL
            {
                'code': '68W',
                'title': 'Combat Medic Specialist',
                'category': 'medical',
                'description': 'Provides emergency medical treatment',
                'min_asvab_score': 101,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Fort Sam Houston, TX',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Combat Medic',
                    '20': 'Senior Combat Medic',
                    '30': 'Medical Sergeant',
                    '40': 'Medical Platoon Sergeant'
                }
            },

            # LOGISTICS & MAINTENANCE
            {
                'code': '92Y',
                'title': 'Unit Supply Specialist',
                'category': 'logistics',
                'description': 'Manages unit supply operations',
                'min_asvab_score': 90,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'moderate',
                'ait_weeks': 12,
                'ait_location': 'Fort Lee, VA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Supply Specialist',
                    '20': 'Senior Supply Specialist',
                    '30': 'Supply Sergeant',
                    '40': 'Supply Operations Sergeant'
                }
            },
            {
                'code': '88M',
                'title': 'Motor Transport Operator',
                'category': 'logistics',
                'description': 'Operates military vehicles',
                'min_asvab_score': 85,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 7,
                'ait_location': 'Fort Leonard Wood, MO',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Motor Transport Operator',
                    '20': 'Senior Motor Transport Operator',
                    '30': 'Motor Transport NCO',
                    '40': 'Motor Transport Platoon Sergeant'
                }
            },
            {
                'code': '91B',
                'title': 'Wheeled Vehicle Mechanic',
                'category': 'maintenance',
                'description': 'Maintains wheeled vehicles',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 13,
                'ait_location': 'Fort Lee, VA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Wheeled Vehicle Mechanic',
                    '20': 'Senior Mechanic',
                    '30': 'Maintenance NCO',
                    '40': 'Motor Pool Sergeant'
                }
            },
            {
                'code': '91A',
                'title': 'M1 Abrams Tank System Maintainer',
                'category': 'maintenance',
                'description': 'Maintains M1 Abrams tanks',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Tank System Maintainer',
                    '20': 'Senior Tank Maintainer',
                    '30': 'Tank Maintenance NCO',
                    '40': 'Tank Maintenance Chief'
                }
            },
            {
                'code': '91M',
                'title': 'Bradley Fighting Vehicle System Maintainer',
                'category': 'maintenance',
                'description': 'Maintains Bradley Fighting Vehicles',
                'min_asvab_score': 87,
                'security_clearance_required': 'none',
                'physical_demand_rating': 'heavy',
                'ait_weeks': 16,
                'ait_location': 'Fort Benning, GA',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'Bradley System Maintainer',
                    '20': 'Senior Bradley Maintainer',
                    '30': 'Bradley Maintenance NCO',
                    '40': 'Bradley Maintenance Chief'
                }
            },

            # ADMINISTRATION
            {
                'code': '42A',
                'title': 'Human Resources Specialist',
                'category': 'administration',
                'description': 'Manages personnel records',
                'min_asvab_score': 90,
                'security_clearance_required': 'secret',
                'physical_demand_rating': 'light',
                'ait_weeks': 10,
                'ait_location': 'Fort Jackson, SC',
                'is_entry_level': True,
                'skill_levels': {
                    '10': 'HR Specialist',
                    '20': 'Senior HR Specialist',
                    '30': 'HR NCO',
                    '40': 'HR Operations Sergeant'
                }
            },
        ]

        # Get the Army branch (assuming it exists)
        try:
            army_branch = Branch.objects.get(name='United States Army')
        except Branch.DoesNotExist:
            self.stdout.write(self.style.ERROR('US Army branch not found. Please create it first.'))
            return

        # Track statistics
        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Create or update MOS entries
        for mos_info in mos_data:
            try:
                mos, created = MOS.objects.update_or_create(
                    code=mos_info['code'],
                    defaults={
                        'title': mos_info['title'],
                        'branch': army_branch,
                        'category': mos_info['category'],
                        'description': mos_info['description'],
                        'min_asvab_score': mos_info['min_asvab_score'],
                        'security_clearance_required': mos_info['security_clearance_required'],
                        'physical_demand_rating': mos_info['physical_demand_rating'],
                        'ait_weeks': mos_info['ait_weeks'],
                        'ait_location': mos_info['ait_location'],
                        'skill_levels': mos_info.get('skill_levels', {}),
                        'is_active': True,
                        'is_entry_level': mos_info.get('is_entry_level', True),
                        'requires_reclassification': mos_info.get('requires_reclassification', False),
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created MOS: {mos_info["code"]} - {mos_info["title"]}'))
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated MOS: {mos_info["code"]} - {mos_info["title"]}')

            except Exception as e:
                skipped_count += 1
                self.stdout.write(self.style.ERROR(f'Error with MOS {mos_info["code"]}: {str(e)}'))

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} MOS entries'))
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count} MOS entries'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} MOS entries'))
        self.stdout.write(self.style.SUCCESS(f'Total processed: {len(mos_data)} MOS entries'))

        # Additional categorization summary
        categories = {}
        for mos_info in mos_data:
            cat = mos_info['category']
            categories[cat] = categories.get(cat, 0) + 1

        self.stdout.write(self.style.SUCCESS(f'\nMOS by Category:'))
        for cat, count in sorted(categories.items()):
            self.stdout.write(f'  {cat}: {count}')

        # Officer vs Enlisted summary
        officer_count = sum(1 for m in mos_data if
                            m['code'].endswith('A') or m['code'].startswith('153') or m['code'] == '60A' or m[
                                'code'] == '90A')
        enlisted_count = len(mos_data) - officer_count
        self.stdout.write(self.style.SUCCESS(f'\nOfficer/Warrant MOS: {officer_count}'))
        self.stdout.write(self.style.SUCCESS(f'Enlisted MOS: {enlisted_count}'))