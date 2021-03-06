# Generated by Django 4.0.4 on 2022-06-04 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_fielddict'),
    ]

    operations = [
        migrations.AddField(
            model_name='fielddict',
            name='model',
            field=models.CharField(blank=True, choices=[('Worker', 'Worker'), ('Location', 'Location'), ('Company', 'Company'), ('Job', 'Job'), ('Operation', 'Operation'), ('ScrapCode', 'ScrapCode'), ('Entry', 'Entry')], default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='fielddict',
            name='name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
