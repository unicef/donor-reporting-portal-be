from django.urls import reverse

from drf_api_checker.pytest import contract, frozenfixture  # noqa

from api_checker import LastModifiedRecorder
from factories import (
    SharePointGroupFactory,
    SharePointLibraryFactory,
    SharePointSiteFactory,
    SharePointTenantFactory,
)


@frozenfixture()
def tenant(request, db):
    return SharePointTenantFactory(url="https://unitst.sharepoint.com/", username=None, password=None)


@frozenfixture()
def site(tenant, request, db):
    return SharePointSiteFactory(
        tenant=tenant,
        name="GLB-DRP",
        site_type="sites",
    )


@frozenfixture()
def library(site, request, db):
    return SharePointLibraryFactory(site=site, name="2020 Certified Reports")


@frozenfixture()
def group(library, request, db):
    return SharePointGroupFactory.create(name="Donors Reports", libs=(library,))


@contract(recorder_class=LastModifiedRecorder)
def test_api_group_list(group, request, django_app, logged_user, theme):
    return reverse("api:sharepoint-group-list")
