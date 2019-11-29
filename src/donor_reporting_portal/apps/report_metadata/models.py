from django.db import models
from django.utils.translation import gettext as _

from model_utils.models import TimeStampedModel
from unicef_security.models import BusinessArea


class Theme(TimeStampedModel):
    """Represents Thematic"""
    name = models.CharField(verbose_name=_("Name"), max_length=64)


class Donor(TimeStampedModel):
    """Represents UNICEF Donors"""

    name = models.CharField(verbose_name=_("Name"), max_length=64)
    code = models.CharField(verbose_name=_("Code"), max_length=16, unique=True)
    us_gov = models.BooleanField(verbose_name=_("Us Government"), default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class ExternalGrant(TimeStampedModel):
    """Represents External Grant"""
    code = models.CharField(verbose_name=_("Code"), max_length=64)
    donor = models.ForeignKey(Donor, verbose_name=_("Donor"), on_delete=models.CASCADE)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} ({self.donor})'


class Grant(TimeStampedModel):
    """Represents the name of a Grant."""
    STANDARD = 'STD'
    THEMATIC = 'THE'
    FFR = 'FFR'
    JPO = 'JPO'

    CATEGORIES = (
        (STANDARD, 'Standard'),
        (THEMATIC, 'Thematic'),
        (FFR, 'Us Gov'),
        (JPO, 'JPO Summary'),
    )

    donor = models.ForeignKey(Donor, verbose_name=_("Donor"), on_delete=models.CASCADE)
    code = models.CharField(verbose_name=_("Code"), max_length=16, unique=True)
    expiry_date = models.DateField(verbose_name=_("Expiry Date"), null=True, blank=True)
    financial_close_date = models.DateField(verbose_name=_("Financial Close Date"), null=True, blank=True)
    business_areas = models.ManyToManyField(BusinessArea, verbose_name=_("Business Areas"), blank=True)
    year = models.CharField(max_length=4, verbose_name=_('Year'))
    theme = models.ForeignKey(Theme, verbose_name=_("Theme"), on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=16, choices=CATEGORIES, verbose_name=_('Category'))
    description = models.CharField(max_length=516, verbose_name=_('Description'), null=True, blank=True)

    class Meta:
        ordering = ['donor']

    def __str__(self):
        return "{}: {}".format(
            self.donor.name,
            self.code
        )
