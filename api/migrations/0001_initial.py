# Generated by Django 5.2.1 on 2025-05-21 16:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('name_common', models.CharField(max_length=100)),
                ('name_official', models.CharField(max_length=200)),
                ('possible_names', models.JSONField(blank=True, default=list)),
                ('region', models.CharField(blank=True, max_length=100)),
                ('capital_name', models.CharField(blank=True, max_length=100)),
                ('capital_latitude', models.FloatField(blank=True, null=True)),
                ('capital_longitude', models.FloatField(blank=True, null=True)),
                ('independent', models.BooleanField(blank=True, null=True)),
                ('google_maps_url', models.URLField(blank=True, max_length=512, null=True)),
                ('open_maps_url', models.URLField(blank=True, max_length=512, null=True)),
                ('flag_png_url', models.URLField(blank=True, max_length=512, null=True)),
                ('flag_svg_url', models.URLField(blank=True, max_length=512, null=True)),
                ('flag_alt_text', models.CharField(blank=True, max_length=200, null=True)),
                ('coat_of_arms_png_url', models.URLField(blank=True, max_length=512, null=True)),
                ('coat_of_arms_svg_url', models.URLField(blank=True, max_length=512, null=True)),
                ('borders', models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name='NameCountryProbability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probability', models.FloatField()),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='name_associations', to='api.country')),
            ],
            options={
                'verbose_name': 'Name-Country probability',
                'verbose_name_plural': 'Name-Country probabilities',
            },
        ),
        migrations.CreateModel(
            name='UniqueName',
            fields=[
                ('name', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('request_count', models.IntegerField(default=1)),
                ('last_accessed_at', models.DateTimeField(auto_now=True)),
                ('associated_countries', models.ManyToManyField(through='api.NameCountryProbability', to='api.country')),
            ],
        ),
        migrations.AddField(
            model_name='namecountryprobability',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_probabilities', to='api.uniquename'),
        ),
        migrations.AlterUniqueTogether(
            name='namecountryprobability',
            unique_together={('name', 'country')},
        ),
    ]
