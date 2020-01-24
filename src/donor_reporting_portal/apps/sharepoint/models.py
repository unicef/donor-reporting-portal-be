from urllib.parse import quote

from django.db import models
from django.utils.translation import gettext as _

from model_utils.models import TimeStampedModel


class SharePointSite(TimeStampedModel):
    url = models.URLField(unique=True)
    name = models.CharField(verbose_name=_("Name"), max_length=32)
    site_type = models.CharField(verbose_name=_("Site Type"), max_length=16, default='sites')
    username = models.CharField(verbose_name=_("Username"), max_length=64, null=True, blank=True)
    password = models.CharField(verbose_name=_("Password"), max_length=64, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'SharePoint Site'
        verbose_name_plural = 'SharePoint Sites'

    def __str__(self):
        return f'{self.url} ({self.name})'

    def relative_url(self):
        return f'{self.site_type}/{self.name}'

    def site_url(self):
        return f'{self.url}{self.site_type}/{self.name}'


class SharePointLibrary(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=64)
    site = models.ForeignKey(SharePointSite, related_name='libraries', on_delete=models.deletion.CASCADE)
    active = models.BooleanField(verbose_name=_("Active"), default=True)
    require_donor_permission = models.BooleanField(verbose_name=_("Require Donor Permission"), default=True)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'site', )
        verbose_name = 'SharePoint Document Library'
        verbose_name_plural = 'SharePoint Document Libraries'

    def __str__(self):
        return f'{self.name} ({self.site.name})'

    @property
    def library_url(self):
        return self.site.url + quote(f'{self.site.site_type}/{self.site.name}/{self.name}')
