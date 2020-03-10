from django.db import models
from django.utils.translation import gettext as _

from model_utils.models import TimeStampedModel
from unicef_sharepoint.models import SharePointLibrary


class SharePointGroup(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=64)
    libraries = models.ManyToManyField(SharePointLibrary, related_name='groups')

    class Meta:
        ordering = ['name']
        verbose_name = 'SharePoint Group'
        verbose_name_plural = 'SharePoint Groups'

    def __str__(self):
        return f'{self.name}'
