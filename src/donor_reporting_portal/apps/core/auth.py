def get_username(strategy, details, backend, user=None, *args, **kwargs):
    return {'username': details.get('email')}
