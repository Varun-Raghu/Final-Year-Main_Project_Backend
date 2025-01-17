# Generated by Django 5.0.3 on 2024-04-12 04:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_landmark_latitude_alter_landmark_longitude"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="profile_pic",
            field=models.URLField(
                default="https://res.cloudinary.com/dybwn1q6h/image/upload/v1712815867/user_opfbgm.png"
            ),
        ),
    ]
