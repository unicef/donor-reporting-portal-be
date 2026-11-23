"""Shared Microsoft Graph client configuration.

Both the API search/download endpoints and the Celery notification tasks need
the same Graph client. Keeping the construction in one place avoids subtle
differences in configuration between web requests and background tasks.
"""

from django.core.exceptions import ImproperlyConfigured

from sharepoint_rest_api import config as sp_config
from sharepoint_rest_api.graph_client import GraphClient


def get_graph_client(folder="Documents"):
    """Return a GraphClient configured for DRP's SharePoint site.

    The tenant is passed explicitly rather than relying on the shared library
    config being read at import time. An empty tenant makes MSAL build the
    invalid authority ``https://login.microsoftonline.com/`` and raise a
    cryptic ValueError, so validate it here with an actionable message.
    """
    tenant = sp_config.GRAPH_TENANT
    if not tenant:
        raise ImproperlyConfigured(
            "GRAPH_TENANT is not configured. Set it to the Azure AD tenant ID "
            "or domain of the app registration used for Microsoft Graph."
        )

    return GraphClient(
        tenant=tenant,
        url=f"{sp_config.SHAREPOINT_TENANT}/{sp_config.SHAREPOINT_SITE_TYPE}/{sp_config.SHAREPOINT_SITE}",
        relative_url=f"{sp_config.SHAREPOINT_SITE_TYPE}/{sp_config.SHAREPOINT_SITE}",
        folder=folder,
    )
