# Generated by Django 4.2.11 on 2024-06-09 15:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_project_id_alter_userprofile_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
