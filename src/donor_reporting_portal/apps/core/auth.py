from social_core.pipeline import social_auth


def social_details(backend, details, response, *args, **kwargs):
    r = social_auth.social_details(backend, details, response, *args, **kwargs)
    r['details']['idp'] = response.get('idp')
    if not r['details'].get('email'):
        if not response.get('email'):
            r['details']['email'] = response["signInNames.emailAddress"]
        else:
            r['details']['email'] = response.get('email')
    email = r['details'].get('email')
    if isinstance(email, str):
        r['details']['email'] = email.lower()
    return r


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    return {'username': details.get('email')}
