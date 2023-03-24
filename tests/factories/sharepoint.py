import factory
from sharepoint_rest_api.models import SharePointLibrary, SharePointSite, SharePointTenant

from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


class SharePointTenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SharePointTenant
        django_get_or_create = ("url",)


class SharePointSiteFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = SharePointSite
        django_get_or_create = ("name",)


class SharePointLibraryFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = SharePointLibrary
        django_get_or_create = ("name",)


class SharePointGroupFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    @factory.post_generation
    def libs(self, create, extracted, **kwargs):
        if not create:
            return  # Simple build, do nothing.

        if extracted:
            for library in extracted:  # A list of groups were passed in, use them
                self.libs.add(library)

    class Meta:
        model = SharePointGroup
        django_get_or_create = ("name",)
