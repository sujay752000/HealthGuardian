# Generated by Django 5.0.3 on 2024-04-17 14:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("doctor", "0002_alter_clinicappointmnettimings_end_time_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="clinicdetails",
            name="consultation_fee",
            field=models.PositiveIntegerField(default=200),
        ),
    ]
