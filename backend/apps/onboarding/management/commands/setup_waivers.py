# backend/apps/onboarding/management/commands/setup_waivers.py
from django.core.management.base import BaseCommand
from apps.onboarding.models import ApplicationWaiverType


class Command(BaseCommand):
    help = 'Sets up initial waiver/acknowledgment types for applications'

    def handle(self, *args, **options):
        waivers = [
            {
                'code': 'code_of_conduct',
                'title': 'Code of Conduct',
                'description': 'Acknowledgment of unit code of conduct',
                'content': """
                I acknowledge and agree to abide by the unit's Code of Conduct, which includes:

                1. **Respect**: Treat all members with respect regardless of rank, experience, or background.
                2. **Integrity**: Act with honesty and integrity in all unit activities.
                3. **Teamwork**: Prioritize team success over individual achievements.
                4. **Communication**: Maintain professional communication in all unit channels.
                5. **Attendance**: Make reasonable efforts to attend scheduled events and notify leadership of absences.
                6. **Security**: Protect unit operational security and sensitive information.
                7. **Representation**: Represent the unit positively in public forums and gaming communities.

                Violation of this code may result in disciplinary action up to and including removal from the unit.
                """,
                'is_required': True,
                'order': 1,
                'waiver_type': 'acknowledgment'
            },
            {
                'code': 'attendance_commitment',
                'title': 'Attendance Commitment',
                'description': 'Commitment to attend mandatory unit events',
                'content': """
                I understand that participation in unit activities is essential for maintaining readiness and cohesion.

                I commit to:
                - Attending mandatory unit events when scheduled
                - Providing advance notice when unable to attend
                - Maintaining minimum monthly participation requirements
                - Participating in my assigned unit's training schedule

                I understand that consistent absence without communication may result in removal from active status.
                """,
                'is_required': True,
                'order': 2,
                'waiver_type': 'agreement'
            },
            {
                'code': 'age_verification',
                'title': 'Age Verification',
                'description': 'Confirmation of minimum age requirement',
                'content': """
                I confirm that I am at least 16 years of age or have parental consent to participate in unit activities.

                I understand that:
                - The unit engages in military simulation gaming
                - Some content may include mature themes
                - Voice communication is required for most activities
                - Parental consent may be requested for members under 18
                """,
                'is_required': True,
                'order': 3,
                'waiver_type': 'consent'
            },
            {
                'code': 'discord_rules',
                'title': 'Discord Server Rules',
                'description': 'Agreement to follow Discord server rules',
                'content': """
                I agree to follow all Discord server rules including:

                1. **No Spam**: Avoid excessive messages, mentions, or promotional content
                2. **Appropriate Content**: No NSFW, offensive, or inappropriate content
                3. **Channel Usage**: Use channels for their designated purposes
                4. **Voice Etiquette**: Maintain professional conduct in voice channels
                5. **No Drama**: Resolve conflicts through proper channels
                6. **Chain of Command**: Respect the unit's command structure

                I understand that violation of Discord rules may result in timeout, kick, or ban.
                """,
                'is_required': True,
                'order': 4,
                'waiver_type': 'agreement'
            },
            {
                'code': 'data_consent',
                'title': 'Data Collection Consent',
                'description': 'Consent for data collection and usage',
                'content': """
                I consent to the collection and use of my data for unit operations including:

                - Discord username and ID for identification
                - Email address for important communications
                - Attendance and participation records
                - Performance metrics in unit activities
                - Application information for unit records

                I understand that:
                - My data will be kept confidential within unit leadership
                - I can request deletion of my data upon leaving the unit
                - Data is used solely for unit management purposes
                """,
                'is_required': True,
                'order': 5,
                'waiver_type': 'consent'
            },
            {
                'code': 'media_release',
                'title': 'Media Release',
                'description': 'Optional consent for media usage',
                'content': """
                I grant permission for the unit to use recordings, screenshots, or streams that may include:

                - My voice in recorded operations or training
                - My username in unit promotional materials
                - Screenshots from unit events I participate in
                - Streaming of operations I'm involved in

                I understand this is OPTIONAL and I can opt-out at any time by notifying unit leadership.
                """,
                'is_required': False,
                'order': 6,
                'waiver_type': 'consent'
            },
            {
                'code': 'training_commitment',
                'title': 'Training Commitment',
                'description': 'Commitment to complete required training',
                'content': """
                I commit to completing required training programs including:

                - Basic Orientation within 7 days of acceptance
                - Branch-specific basic training within 30 days
                - Maintaining required certifications for my position
                - Participating in ongoing unit training exercises

                I understand that failure to complete required training may affect my eligibility for positions or promotions.
                """,
                'is_required': True,
                'order': 7,
                'waiver_type': 'agreement'
            },
            {
                'code': 'mod_usage',
                'title': 'Modification Usage Agreement',
                'description': 'Agreement regarding game modifications',
                'content': """
                I understand and agree that:

                - The unit may require specific game modifications for operations
                - I am responsible for properly installing required mods
                - Use of unauthorized mods during unit operations is prohibited
                - Cheating, hacking, or exploiting is strictly forbidden
                - Technical support for mods is provided on a best-effort basis

                I will maintain required modifications and keep them updated as directed.
                """,
                'is_required': True,
                'order': 8,
                'waiver_type': 'agreement'
            }
        ]

        created_count = 0
        updated_count = 0

        for waiver_data in waivers:
            waiver, created = ApplicationWaiverType.objects.update_or_create(
                code=waiver_data['code'],
                defaults=waiver_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created waiver type: {waiver.title}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated waiver type: {waiver.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully processed {len(waivers)} waiver types: '
                f'{created_count} created, {updated_count} updated'
            )
        )