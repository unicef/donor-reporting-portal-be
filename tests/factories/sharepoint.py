import factory

from donor_reporting_portal.apps.sharepoint.models import SharePointLibrary, SharePointSite


class SharePointSiteFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = SharePointSite
        django_get_or_create = ('name',)


class SharePointLibraryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = SharePointLibrary
        django_get_or_create = ('name',)
