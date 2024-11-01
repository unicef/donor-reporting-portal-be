from ..settings import env

MATOMO_SITE_TRACKER = env("MATOMO_SITE_TRACKER", default="https://unisitetracker.unicef.io/")
MATOMO_SITE_ID = env("MATOMO_SITE_ID", default=None)
