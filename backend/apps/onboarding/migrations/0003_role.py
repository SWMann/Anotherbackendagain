# Generated migration file (e.g., 0002_add_recruitment_slots.py)
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),  # or whatever your units migration is
        ('onboarding', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='selected_recruitment_slot',
            field=models.ForeignKey(blank=True, help_text='The recruitment slot/position applied for', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applications', to='units.recruitmentslot'),
        ),
        migrations.AddField(
            model_name='application',
            name='alternate_recruitment_slot_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alternate1_applications', to='units.recruitmentslot'),
        ),
        migrations.AddField(
            model_name='application',
            name='alternate_recruitment_slot_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alternate2_applications', to='units.recruitmentslot'),
        ),
        # Add any other missing fields like application_number, dates, etc.
    ]