from django.conf import settings

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ConfigAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Return All Static values used for drop-down in the frontend"""

        return Response(
            {
                'tracker': {
                    'site_tracker': settings.MATOMO_SITE_TRACKER,
                    'site_id': settings.MATOMO_SITE_ID
                },
                'source_id': settings.DRP_SOURCE_IDS
            },
            status=status.HTTP_200_OK
        )
