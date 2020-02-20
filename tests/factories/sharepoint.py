import factory
from unicef_sharepoint.models import SharePointLibrary, SharePointSite, SharePointTenant


class SharePointTenantFactory(factory.DjangoModelFactory):

    class Meta:
        model = SharePointTenant
        django_get_or_create = ('url',)


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
