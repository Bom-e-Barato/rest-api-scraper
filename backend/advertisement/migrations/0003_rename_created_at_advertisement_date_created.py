# Generated by Django 4.0.5 on 2022-06-03 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advertisement', '0002_alter_advertisement_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advertisement',
            old_name='created_at',
            new_name='date_created',
        ),
    ]