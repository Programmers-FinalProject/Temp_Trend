# Generated by Django 4.1 on 2024-07-31 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0015_alter_musinsadata_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationrecord',
            name='session',
            field=models.CharField(default='unknown', max_length=255),
            preserve_default=False,
        ),
    ]
