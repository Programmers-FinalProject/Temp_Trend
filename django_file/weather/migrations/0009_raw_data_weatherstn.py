# Generated by Django 4.1 on 2024-07-25 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0008_alter_weatherdata_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='raw_data_WeatherStn',
            fields=[
                ('stn', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('lon', models.DecimalField(decimal_places=6, max_digits=9)),
                ('lat', models.DecimalField(decimal_places=6, max_digits=9)),
                ('stn_sp', models.CharField(max_length=100)),
                ('ht', models.DecimalField(decimal_places=2, max_digits=6)),
                ('ht_pa', models.DecimalField(decimal_places=2, max_digits=6)),
                ('ht_ta', models.DecimalField(decimal_places=2, max_digits=6)),
                ('ht_wd', models.DecimalField(decimal_places=2, max_digits=6)),
                ('ht_rn', models.DecimalField(decimal_places=2, max_digits=6)),
                ('stn_ko', models.CharField(max_length=100)),
                ('stn_en', models.CharField(max_length=100)),
                ('fct_id', models.CharField(max_length=100)),
                ('law_id', models.CharField(max_length=100)),
                ('basin', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'raw_data.weather_stn',
                'managed': False,
            },
        ),
    ]
