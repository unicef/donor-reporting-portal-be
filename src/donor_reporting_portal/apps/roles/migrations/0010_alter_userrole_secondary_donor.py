# Generated by Django 4.0.5 on 2022-06-08 06:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("report_metadata", "0011_remove_grant_business_areas"),
        ("roles", "0009_auto_20220511_1724"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userrole",
            name="secondary_donor",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_roles",
                to="report_metadata.secondarydonor",
            ),
        ),
    ]
