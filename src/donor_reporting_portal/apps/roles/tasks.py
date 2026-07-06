import time
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.timezone import now

from celery.utils.log import get_task_logger
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from sharepoint_rest_api.graph_client import GraphClient
from unicef_notification.utils import send_notification_with_template

from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSharePointSearchSerializer,
    GaviSharePointSearchSerializer,
)
from donor_reporting_portal.apps.report_metadata.models import Donor
from donor_reporting_portal.apps.roles.models import UserRole
from donor_reporting_portal.config.celery import app

logger = get_task_logger(__name__)


class Notifier:
    donor_code = None
    serializer = None
    template_name = None
    group_name = None
    page_size = 500

    def __init__(self, donor_code):
        self.donor = Donor.objects.get(code=donor_code)

    def get_notify_periods(self):
        return [
            x
            for x in [
                (
                    UserRole.EVERY_MONTH,
                    today().replace(day=1) - relativedelta(months=1),
                    today().day == 1,
                ),
                (UserRole.EVERY_MONDAY, today() - timedelta(7), today().weekday() == 0),
                (UserRole.EVERY_DAY, today(), True),
            ]
            if x[2]
        ]

    def get_filter_dict(self, modified_date):
        return {}

    def get_searchable_properties(self):
        return set()

    def get_reverse_map(self):
        if self.serializer:
            return self.serializer.get_property_name_reverse()
        return None

    def notify(self):
        client = GraphClient()

        notification_periods = self.get_notify_periods()

        for period, modified_date, _ in notification_periods:
            filters = self.get_filter_dict(modified_date)
            searchable_properties = self.get_searchable_properties()
            reverse_map = self.get_reverse_map()
            page = 1
            exit_condition = True
            reports = []

            users = self.get_queryset(period)

            if users:
                while exit_condition:
                    response, total_rows = client.search(
                        search=None,
                        filters=filters,
                        page=page,
                        searchable_properties=searchable_properties,
                        reverse_map=reverse_map,
                        page_size=self.page_size,
                    )
                    exit_condition = page * self.page_size < total_rows
                    page += 1
                    qs = self.serializer(response, many=True)
                    reports.extend(qs.data)

                if reports:
                    context = {"reports": reports, "donor": self.donor.name, "group_name": self.group_name}
                    recipients = list({str(user["user__email"]) for user in users if user["user__email"]})
                    send_notification_with_template(recipients, self.template_name, context)


class DonorNotifier(Notifier):
    serializer = DRPSharePointSearchSerializer
    template_name = "notify_donor"

    document_type_filter = [
        "Certified Financial Statement - EC",
        "Certified Financial Statement - US Government",
        "Certified Statement of Account",
        "Certified Statement of Account EU",
        "Certified Statement of Account JPO",
        "Donor Statement CERF",
        "Certified Financial Report - Final",
        "Certified Financial Report - Interim",
        "Donor Statement Innovation",
        "Donor Statement Joint Programme",
        "Donor Statement Joint Programme PUNO",
        "Donor Statement JPO Summary",
        "Donor Statement Trust Fund",
        "Donor Statement UN",
        "Donor Statement UNICEF Hosted Funds",
        "FFR Form (SF-425)",
        "JPO Expenditure Summary",
        "Statement of Account Thematic Funds",
        "Donor Statement by Activity",
        "Interim Statement by Nature of expense",
        "Funds Request Report",
        "Non-Standard Statement",
        "Emergency Consolidated - Final",
        "Emergency  Consolidated - Interim",
        "Thematic Emergency Global - Final",
        "Thematic Emergency Global - Interim",
        "Emergency - Two Pager",
        "Emergency - Final",
        "Emergency - Interim",
        "Human Interest / Photos",
        "Narrative - Final",
        "Narrative - Interim",
        "Narrative Consolidated - Final",
        "Narrative Consolidated - Interim",
        "Thematic Consolidated - Final",
        "Thematic Consolidated - Interim",
        "Thematic Global - Final",
        "Thematic Global - Interim",
        "Thematic - Final",
        "Thematic - Interim",
        "Short Summary Update",
        "Official Receipts",
        "Quarterly Monitoring Report",
    ]

    def get_filter_dict(self, modified_date):
        return {
            "Donor": self.donor.code,
            "DonorDocument": ",".join(self.document_type_filter),
            "Modified__gte": modified_date.strftime("%Y-%m-%d"),
        }

    def get_searchable_properties(self):
        return {"Donor", "DonorDocument", "Modified"}

    def get_queryset(self, period):
        return UserRole.objects.filter(donor=self.donor, notification_period=period).values(
            "user__first_name", "user__email"
        )


class GaviNotifier(Notifier):
    serializer = GaviSharePointSearchSerializer
    template_name = "notify_gavi"

    def __init__(self, donor_code, group_name, specific_date=None):
        self.donor = Donor.objects.get(code=donor_code)
        self.group_name = group_name
        self.specific_date = specific_date

    def get_queryset(self, period):
        return UserRole.objects.filter(
            donor=self.donor, notification_period=period, group__name=self.group_name
        ).values("user__first_name", "user__email")

    def get_filter_dict(self, modified_date):
        date = self.specific_date or modified_date.strftime("%Y-%m-%d")
        return {
            "Modified": date,
            "MOUReference": self.group_name,
            "Urgent__not": "Yes",
        }

    def get_searchable_properties(self):
        return {"Modified", "MOUReference", "Urgent"}


class GaviUrgentNotifier(GaviNotifier):
    template_name = "notify_urgent_gavi"

    def get_notify_periods(self):
        return [
            (UserRole.EVERY_DAY, now() - timedelta(seconds=3600), True),
        ]

    def get_filter_dict(self, modified_date):
        return {
            "Modified__gte": modified_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "MOUReference": self.group_name,
            "Urgent": "Yes",
        }

    def get_searchable_properties(self):
        return {"Modified", "MOUReference", "Urgent"}


@app.task
def notify_donor(donor_code):
    """Notify one donor."""
    logger.info(f"Notifying {donor_code}")
    notifier = DonorNotifier(donor_code)
    notifier.notify()


@app.task
def notify_gavi_donor(donor_code=settings.GAVI_DONOR_CODE, specific_date=None):
    """Notify GAVI and spawn one task per group."""
    logger.info("Notifying GAVI")
    for group_name in Group.objects.filter(name__startswith="MOU").values_list("name", flat=True):
        notify_gavi_donor_ctn.delay(donor_code, group_name.strip(), specific_date)
        time.sleep(5)


@app.task
def notify_gavi_donor_ctn(donor_code, group_name, specific_date=None):
    """Notify a GAVI group."""
    logger.info(f"Notifying {donor_code}")
    notifier = GaviNotifier(donor_code, group_name, specific_date=specific_date)
    notifier.notify()


@app.task
def notify_new_records():
    logger.info("Notify Start")
    for donor_code in Donor.objects.filter(active=True).values_list("code", flat=True):
        if donor_code == settings.GAVI_DONOR_CODE:
            notify_gavi_donor(donor_code)
        else:
            notify_donor.delay(donor_code)


@app.task
def notify_urgent_by_group(group_name):
    """Notify a GAVI group."""
    notifier = GaviUrgentNotifier(settings.GAVI_DONOR_CODE, group_name)
    notifier.notify()


@app.task
def notify_urgent_records():
    """Notify GAVI urgent records and spawn one task per group."""
    logger.info("Notify Urgent CTNs Start")
    for group_name in Group.objects.filter(name__startswith="MOU").values_list("name", flat=True):
        notify_urgent_by_group.delay(group_name)
        time.sleep(5)
