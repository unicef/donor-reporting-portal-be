# Generated by Django 2.2.6 on 2019-10-07 16:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("roles", "0002_auto_20190920_0339"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="userrole",
            options={
                "permissions": (("can_view_all_donors", "Can views all Donors"),),
                "verbose_name": "User Role",
                "verbose_name_plural": "User Roles",
            },
        ),
    ]
