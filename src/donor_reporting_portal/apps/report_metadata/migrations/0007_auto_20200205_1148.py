# Generated by Django 2.2.8 on 2020-02-05 17:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("report_metadata", "0006_donor_us_gov"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="theme",
            options={"ordering": ["name"]},
        ),
    ]
