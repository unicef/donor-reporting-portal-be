# Generated by Django 2.2.6 on 2019-11-04 17:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SharePointSite",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=32, unique=True, verbose_name="Name"),
                ),
                ("url", models.URLField()),
                (
                    "wrapper_name",
                    models.CharField(max_length=16, unique=True, verbose_name="Wrapper"),
                ),
            ],
            options={
                "verbose_name": "SharePoint Site",
                "verbose_name_plural": "SharePoint Sites",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SharePointLibrary",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("name", models.CharField(max_length=32, verbose_name="Name")),
                ("active", models.BooleanField(default=True, verbose_name="Active")),
                ("username", models.CharField(max_length=64, verbose_name="Username")),
                ("password", models.CharField(max_length=64, verbose_name="Password")),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="libraries",
                        to="sharepoint.SharePointSite",
                    ),
                ),
            ],
            options={
                "verbose_name": "SharePoint Document Library",
                "verbose_name_plural": "SharePoint Document Libraries",
                "ordering": ["name"],
                "unique_together": {("name", "site")},
            },
        ),
    ]
