# Generated by Django 3.2.18 on 2023-04-23 13:23

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20230422_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.vehicle_image_file_path),
        ),
    ]