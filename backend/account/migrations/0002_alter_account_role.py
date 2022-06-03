# Generated by Django 4.0.2 on 2022-03-02 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(2, 'Teacher'), (1, 'Student'), (0, 'Deleted')]),
        ),
    ]