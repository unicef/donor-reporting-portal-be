from django.conf import settings

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from donor_reporting_portal.api.cache import CONFIG_NAMESPACE, scoped_get


class ConfigAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Return All Static values used for drop-down in the frontend."""
        data = scoped_get(
            request,
            CONFIG_NAMESPACE,
            lambda: {
                "tracker": {
                    "site_tracker": settings.MATOMO_SITE_TRACKER,
                    "site_id": settings.MATOMO_SITE_ID,
                },
                "source_id": settings.DRP_SOURCE_IDS,
                "gavi_donor_code": settings.GAVI_DONOR_CODE,
            },
            timeout=None,
        )
        return Response(data, status=status.HTTP_200_OK)
