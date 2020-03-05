from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

import rest_framework_jwt.views


class UNICEFLogoutView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return f'https://login.microsoftonline.com/{settings.TENANT_ID}' \
               f'/oauth2/logout?post_logout_redirect_uri={settings.HOST}{settings.LOGOUT_URL}'


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'api-token-auth/', rest_framework_jwt.views.obtain_jwt_token),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'social/unicef-logout/', UNICEFLogoutView.as_view()),
    path(r'social', include('social_django.urls', namespace='social')),
    path(r'api/', include('donor_reporting_portal.api.urls', namespace='api')),
    path(r'api/', include('unicef_sharepoint.urls', namespace='sharepoint')),
    path(r'accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ]
