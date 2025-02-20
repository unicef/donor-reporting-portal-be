import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ""

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            dest="all",
            default=False,
            help="select all options but `demo`",
        )

        parser.add_argument(
            "--collectstatic",
            action="store_true",
            dest="collectstatic",
            default=False,
            help="",
        )

        parser.add_argument(
            "--stale_ct",
            action="store_true",
            dest="stale_ct",
            default=False,
            help="",
        )

        parser.add_argument(
            "--permissions",
            action="store_true",
            dest="permissions",
            default=False,
            help="",
        )

        parser.add_argument(
            "--with-check",
            action="store_true",
            dest="check",
            default=False,
            help="Run checks",
        )

        parser.add_argument("--users", action="store_true", dest="users", default=False, help="")

        parser.add_argument("--metadata", action="store_true", dest="metadata", default=False, help="")

        parser.add_argument(
            "--migrate",
            action="store_true",
            dest="migrate",
            default=False,
            help="select all production deployment options",
        )

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        migrate = options["migrate"]
        _all = options["all"]
        ModelUser = get_user_model()  # noqa
        if options["collectstatic"] or _all:
            self.stdout.write("Run collectstatic")
            call_command("collectstatic", verbosity=verbosity - 1, interactive=False)

        if migrate or _all:
            self.stdout.write("Run migrations")
            call_command("migrate", verbosity=verbosity - 1)

        if options["users"] or _all:
            call_command("update_notifications", verbosity=verbosity - 1)
            pwd = os.environ.get("ADMIN_PASSWORD")
            admin = os.environ.get("ADMIN_USERNAME", "admin")

            if pwd:
                _, created = ModelUser.objects.get_or_create(
                    username=admin,
                    defaults={
                        "is_superuser": True,
                        "is_staff": True,
                        "password": make_password(pwd),
                    },
                )

                if created:  # pragma: no cover
                    self.stdout.write(f"Created superuser `{admin}` with password `{pwd}`")
                else:  # pragma: no cover
                    self.stdout.write(f"Superuser `{admin}` already exists`.")

        if options["stale_ct"] or _all:
            call_command("remove_stale_contenttypes", verbosity=verbosity - 1, interactive=False)

        if options["permissions"] or _all:
            call_command("update_permissions", verbosity=verbosity - 1)

        if options["metadata"] or _all:
            call_command("loaddata", "groups.json")
            call_command("loaddata", "libraries.json")
            call_command("loaddata", "metadata.json")
