# Generated by Django 2.2.8 on 2019-12-31 14:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sharepoint", "0004_auto_20191105_1400"),
    ]

    operations = [
        migrations.AddField(
            model_name="sharepointlibrary",
            name="require_donor_permission",
            field=models.BooleanField(
                default=True, verbose_name="Require Donor Permission"
            ),
        ),
    ]
