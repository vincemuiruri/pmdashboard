# Generated by Django 5.1.4 on 2025-03-15 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_projectmanager_about_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectphase',
            unique_together={('project', 'phase_number')},
        ),
        migrations.AlterUniqueTogether(
            name='projectprogress',
            unique_together={('project', 'phase')},
        ),
    ]
