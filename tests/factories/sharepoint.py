import factory
from unicef_sharepoint.models import SharePointLibrary, SharePointSite, SharePointTenant

from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


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


class SharePointGroupFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    @factory.post_generation
    def libraries(self, create, extracted, **kwargs):
        if not create:
            return  # Simple build, do nothing.

        if extracted:
            for library in extracted:  # A list of groups were passed in, use them
                self.libraries.add(library)

    class Meta:
        model = SharePointGroup
        django_get_or_create = ('name',)
