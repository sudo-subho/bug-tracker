# Generated by Django 4.2.11 on 2024-06-11 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_userprofile_address_alter_project_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mobile',
            field=models.IntegerField(default='0'),
        ),
    ]
