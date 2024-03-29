# Generated by Django 2.2.8 on 2020-01-24 16:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sharepoint", "0005_sharepointlibrary_require_donor_permission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sharepointsite",
            name="name",
            field=models.CharField(max_length=32, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="sharepointsite",
            name="url",
            field=models.URLField(unique=True),
        ),
    ]
