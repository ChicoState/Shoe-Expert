# Generated by Django 4.2 on 2023-04-07 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RunningShoe',
            fields=[
                ('shoe_name', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('arch_type', models.CharField(blank=True, max_length=32, null=True)),
                ('brand', models.CharField(blank=True, max_length=32, null=True)),
                ('cushioning', models.CharField(blank=True, max_length=32, null=True)),
                ('distance', models.CharField(blank=True, max_length=128, null=True)),
                ('features', models.CharField(blank=True, max_length=256, null=True)),
                ('flexibility', models.CharField(blank=True, max_length=32, null=True)),
                ('forefoot_height', models.CharField(blank=True, max_length=8, null=True)),
                ('heel_height', models.CharField(blank=True, max_length=8, null=True)),
                ('heel_toe_drop', models.CharField(blank=True, max_length=8, null=True)),
                ('msrp', models.CharField(blank=True, max_length=8, null=True)),
                ('pronation', models.CharField(blank=True, max_length=256, null=True)),
                ('release_date', models.CharField(blank=True, max_length=128, null=True)),
                ('strike_pattern', models.CharField(blank=True, max_length=128, null=True)),
                ('technology', models.CharField(blank=True, max_length=128, null=True)),
                ('terrain', models.CharField(blank=True, max_length=32, null=True)),
                ('toebox', models.CharField(blank=True, max_length=32, null=True)),
                ('use', models.CharField(blank=True, max_length=128, null=True)),
                ('waterproofing', models.CharField(blank=True, max_length=32, null=True)),
                ('weight', models.CharField(blank=True, max_length=8, null=True)),
                ('width', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
    ]
