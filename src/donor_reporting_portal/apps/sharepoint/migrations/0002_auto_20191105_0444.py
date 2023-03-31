# Generated by Django 2.2.6 on 2019-11-05 10:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sharepoint", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sharepointlibrary",
            name="password",
        ),
        migrations.RemoveField(
            model_name="sharepointlibrary",
            name="username",
        ),
        migrations.AddField(
            model_name="sharepointsite",
            name="password",
            field=models.CharField(
                blank=True, max_length=64, null=True, verbose_name="Password"
            ),
        ),
        migrations.AddField(
            model_name="sharepointsite",
            name="username",
            field=models.CharField(
                blank=True, max_length=64, null=True, verbose_name="Username"
            ),
        ),
    ]
