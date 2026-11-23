from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Core"

    def ready(self):
        from donor_reporting_portal.libs.cache import register_cache_signals  # noqa: PLC0415

        register_cache_signals()
