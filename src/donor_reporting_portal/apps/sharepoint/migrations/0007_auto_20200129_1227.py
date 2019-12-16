# Generated by Django 2.2.8 on 2020-01-29 18:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sharepoint', '0006_auto_20200124_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharePointTenant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('url', models.URLField(unique=True)),
                ('username', models.CharField(blank=True, max_length=64, null=True, verbose_name='Username')),
                ('password', models.CharField(blank=True, max_length=64, null=True, verbose_name='Password')),
            ],
            options={
                'verbose_name': 'SharePoint Tenant',
                'verbose_name_plural': 'SharePoint Tenants',
                'ordering': ['url'],
            },
        ),
        migrations.RemoveField(
            model_name='sharepointsite',
            name='password',
        ),
        migrations.RemoveField(
            model_name='sharepointsite',
            name='url',
        ),
        migrations.RemoveField(
            model_name='sharepointsite',
            name='username',
        ),
        migrations.AlterField(
            model_name='sharepointsite',
            name='site_type',
            field=models.CharField(choices=[('sites', 'sites'), ('teams', 'teams')], default='sites', max_length=16, verbose_name='Site Type'),
        ),
        migrations.AddField(
            model_name='sharepointsite',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sites', to='sharepoint.SharePointTenant'),
        ),
    ]