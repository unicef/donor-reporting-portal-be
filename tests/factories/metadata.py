import factory

from donor_reporting_portal.apps.report_metadata.models import (
    Donor,
    DRPMetadata,
    ExternalGrant,
    Grant,
    SecondaryDonor,
    Theme,
)


class ThemeFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = Theme
        django_get_or_create = ("name",)


class DonorFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)

    class Meta:
        model = Donor
        django_get_or_create = ("code",)


class ExternalGrantFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)
    donor = factory.SubFactory(DonorFactory)

    class Meta:
        model = ExternalGrant
        django_get_or_create = ("code",)


class GrantFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)
    donor = factory.SubFactory(DonorFactory)

    class Meta:
        model = Grant
        django_get_or_create = ("code",)


class SecondaryDonorFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)

    class Meta:
        model = SecondaryDonor
        django_get_or_create = ("code",)


class DRPMetadataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DRPMetadata
