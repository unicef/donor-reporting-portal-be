from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured

from donor_reporting_portal.libs.graph import get_graph_client
from sharepoint_rest_api import config as sp_config


def test_get_graph_client_uses_shared_configuration():
    tenant = "test-tenant"
    with (
        mock.patch.object(sp_config, "GRAPH_TENANT", tenant),
        mock.patch("donor_reporting_portal.libs.graph.GraphClient") as client_cls,
    ):
        client = get_graph_client(folder="Reports")

    client_cls.assert_called_once_with(
        tenant=tenant,
        url=f"{sp_config.SHAREPOINT_TENANT}/{sp_config.SHAREPOINT_SITE_TYPE}/{sp_config.SHAREPOINT_SITE}",
        relative_url=f"{sp_config.SHAREPOINT_SITE_TYPE}/{sp_config.SHAREPOINT_SITE}",
        folder="Reports",
    )
    assert client is client_cls.return_value


def test_get_graph_client_rejects_empty_tenant():
    with (
        mock.patch.object(sp_config, "GRAPH_TENANT", ""),
        mock.patch("donor_reporting_portal.libs.graph.GraphClient") as client_cls,
    ):
        with pytest.raises(ImproperlyConfigured, match="GRAPH_TENANT"):
            get_graph_client()

    client_cls.assert_not_called()
