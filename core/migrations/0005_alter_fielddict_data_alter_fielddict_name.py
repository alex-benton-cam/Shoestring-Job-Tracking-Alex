# Generated by Django 4.0.4 on 2022-06-04 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_fielddict_model_fielddict_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fielddict',
            name='data',
            field=models.TextField(default='{}'),
        ),
        migrations.AlterField(
            model_name='fielddict',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
