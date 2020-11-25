from social_core.pipeline.user import USER_FIELDS


# replace with create_unicef_user in unicef-security when v0.5 is released
def create_unicef_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not (fields and details.get('email', '').endswith('@unicef.org')):
        return

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }
