# Generated by Django 2.2.7 on 2019-11-29 19:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("report_metadata", "0005_auto_20191014_0955"),
    ]

    operations = [
        migrations.AddField(
            model_name="donor",
            name="us_gov",
            field=models.BooleanField(default=False, verbose_name="Us Gov Flag"),
        ),
    ]
