from django.conf import settings
from django.http import HttpResponseRedirect

from social_core.exceptions import AuthCanceled, AuthMissingParameter
from social_django.middleware import SocialAuthExceptionMiddleware
from unicef_security.backends import UnicefAzureADBBCOAuth2


class UnicefSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    """Middleware to ignore Forgot Password Exceptions"""

    def process_exception(self, request, exception):
        if isinstance(exception, (AuthCanceled, AuthMissingParameter)):
            return HttpResponseRedirect(self.get_redirect_uri(request, exception))
        else:
            raise exception

    def get_redirect_uri(self, request, exception):
        error = request.GET.get('error', None)

        # This is what we should expect:
        # ['AADB2C90118: The user has forgotten their password.\r\n
        # Correlation ID: 7e8c3cf9-2fa7-47c7-8924-a1ea91137ba9\r\n
        # Timestamp: 2018-11-13 11:37:56Z\r\n']
        error_description = request.GET.get('error_description', None)
        if error == "access_denied" and error_description is not None:
            if 'AADB2C90118' in error_description:
                auth_class = UnicefAzureADBBCOAuth2()
                redirect_home = auth_class.get_redirect_uri()
                breakpoint()
                redirect_url = 'https://login.microsoftonline.com/' + \
                               settings.TENANT_ID + \
                               "/oauth2/v2.0/authorize?p=" + \
                               settings.SOCIAL_PASSWORD_RESET_POLICY + \
                               "&client_id=" + settings.KEY + \
                               "&nonce=defaultNonce&redirect_uri=" + redirect_home + \
                               "&scope=openid+email&response_type=code"
                return redirect_url

        # TODO: In case of password reset the state can't be verified figure out a way to log the user in after reset
        return settings.LOGIN_URL