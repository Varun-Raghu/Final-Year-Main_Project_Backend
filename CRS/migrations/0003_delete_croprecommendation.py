# Generated by Django 5.0.3 on 2024-04-29 08:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("CRS", "0002_remove_croprecommendation_landid"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CropRecommendation",
        ),
    ]
