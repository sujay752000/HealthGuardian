# Generated by Django 5.0.3 on 2024-04-15 17:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("doctor", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="clinicappointmnettimings",
            name="end_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="clinicappointmnettimings",
            name="start_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="onlineconsultationtimings",
            name="end_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="onlineconsultationtimings",
            name="start_time",
            field=models.TimeField(blank=True, null=True),
        ),
    ]
