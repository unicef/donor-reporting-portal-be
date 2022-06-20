from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import token_obtain_pair

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api-token-auth/', token_obtain_pair),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'security/', include('unicef_security.urls')),
    path(r'social/', include('social_django.urls', namespace='social')),
    path(r'api/', include('donor_reporting_portal.api.urls', namespace='api')),
    path(r'api/', include('sharepoint_rest_api.urls', namespace='sharepoint')),
    path(r'accounts/', include('django.contrib.auth.urls')),
    path(r'manage/adminactions/', include('adminactions.urls')),
    path(r'manage/impersonate/', include('impersonate.urls')),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
