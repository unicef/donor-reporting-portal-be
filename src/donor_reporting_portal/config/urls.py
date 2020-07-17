from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

import rest_framework_jwt.views
from unicef_security.views import UNICEFLogoutView

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api-token-auth/', rest_framework_jwt.views.obtain_jwt_token),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'social/unicef-logout/', UNICEFLogoutView.as_view()),
    path(r'social', include('social_django.urls', namespace='social')),
    path(r'api/', include('donor_reporting_portal.api.urls', namespace='api')),
    path(r'api/', include('sharepoint_rest_api.urls', namespace='sharepoint')),
    path(r'accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
