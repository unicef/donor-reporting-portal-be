from datetime import timedelta

from celery.utils.log import get_task_logger
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from sharepoint_rest_api import config
from sharepoint_rest_api.client import SharePointClient
from sharepoint_rest_api.config import SHAREPOINT_PAGE_SIZE
from sharepoint_rest_api.utils import to_camel
from unicef_notification.utils import send_notification_with_template

from donor_reporting_portal.api.serializers.sharepoint import DRPSharePointSearchSerializer
from donor_reporting_portal.apps.report_metadata.models import Donor
from donor_reporting_portal.apps.roles.models import UserRole
from donor_reporting_portal.config import settings
from donor_reporting_portal.config.celery import app

logger = get_task_logger(__name__)


@app.task
def notify_donor(donor_code):

    document_type_filter = 'Narrative%20Consolidated%20-%20Interim,Agreements'

    donor = Donor.objects.get(code=donor_code)
    logger.info(f'Notifing {donor.name}')
    client = SharePointClient(url=f'{config.SHAREPOINT_TENANT}/{config.SHAREPOINT_SITE_TYPE}/{config.SHAREPOINT_SITE}')

    notification_periods = [x for x in [
        (UserRole.EVERY_MONTH, today().replace(day=1) - relativedelta(months=1), today().day == 1),
        (UserRole.EVERY_MONDAY, today() - timedelta(7), today().weekday() == 0),
        (UserRole.EVERY_DAY, today() - timedelta(1), True),
    ] if x[2]]

    for period, modified_date, _ in notification_periods:
        filters = {
            'DRPDonorCode': donor.code,
            'DonorDocument': document_type_filter,
            'DRPModified__gte': modified_date.strftime('%Y-%m-%d')
        }
        serializer_fields = DRPSharePointSearchSerializer._declared_fields.keys()
        selected = ['DRP' + to_camel(x) for x in serializer_fields] + ["Title", "Author", "Path"]

        page = 1
        exit_condition = True
        reports = []
        while exit_condition:
            response, total_rows = client.search(
                filters=filters,
                select=selected,
                source_id=settings.DRP_SOURCE_IDS['external'],
                page=page
            )
            exit_condition = page * SHAREPOINT_PAGE_SIZE < total_rows
            page += 1
            qs = DRPSharePointSearchSerializer(response, many=True)
            reports.extend(qs.data)

        if reports:
            users = UserRole.objects.filter(donor=donor, notification_period=period).values(
                'user__first_name', 'user__email')
            context = {'reports': reports}
            send_notification_with_template([user['user__email'] for user in users], 'notify_donor', context)


@app.task
def notify_new_records():
    logger.info('Notify Start')
    for donor_code in Donor.objects.filter(active=True).values_list('code', flat=True):
        notify_donor.delay(donor_code)
