import factory

from donor_reporting_portal.apps.report_metadata.models import Donor, ExternalGrant, Grant, SecondaryDonor, Theme


class ThemeFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = Theme
        django_get_or_create = ('name',)


class DonorFactory(factory.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)

    class Meta:
        model = Donor
        django_get_or_create = ('code',)


class ExternalGrantFactory(factory.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)
    donor = factory.SubFactory(DonorFactory)

    class Meta:
        model = ExternalGrant
        django_get_or_create = ('code',)


class GrantFactory(factory.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)
    donor = factory.SubFactory(DonorFactory)

    class Meta:
        model = Grant
        django_get_or_create = ('code',)


class SecondaryDonorFactory(factory.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)

    class Meta:
        model = SecondaryDonor
        django_get_or_create = ('code',)
