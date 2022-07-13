from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group

from celery.utils.log import get_task_logger
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from sharepoint_rest_api import config
from sharepoint_rest_api.client import SharePointClient
from sharepoint_rest_api.config import SHAREPOINT_PAGE_SIZE
from sharepoint_rest_api.utils import to_camel
from unicef_notification.utils import send_notification_with_template

from donor_reporting_portal.api.serializers.fields import CTNSearchMultiSharePointField, CTNSearchSharePointField
from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSharePointSearchSerializer,
    GaviSharePointSearchSerializer,
)
from donor_reporting_portal.apps.report_metadata.models import Donor
from donor_reporting_portal.apps.roles.models import UserRole
from donor_reporting_portal.config.celery import app

logger = get_task_logger(__name__)


@app.task
def notify_donor(donor_code):

    document_type_filter = [
        'Certified Financial Statement - EC',
        'Certified Financial Statement - US Government',
        'Certified Statement of Account',
        'Certified Statement of Account EU',
        'Certified Statement of Account JPO',
        'Donor Statement CERF',
        'Certified Financial Report - Final',
        'Certified Financial Report - Interim',
        'Donor Statement Innovation',
        'Donor Statement Joint Programme',
        'Donor Statement Joint Programme PUNO',
        'Donor Statement JPO Summary',
        'Donor Statement Trust Fund',
        'Donor Statement UN',
        'Donor Statement UNICEF Hosted Funds',
        'FFR Form (SF-425)',
        'JPO Expenditure Summary',
        'Statement of Account Thematic Funds',
        'Donor Statement by Activity',
        'Interim Statement by Nature of expense',
        'Funds Request Report',
        'Non-Standard Statement',
        'Emergency Consolidated - Final',
        'Emergency  Consolidated - Interim',
        'Thematic Emergency Global - Final',
        'Thematic Emergency Global - Interim',
        'Emergency - Two Pager',
        'Emergency - Final',
        'Emergency - Interim',
        'Human Interest / Photos',
        'Narrative - Final',
        'Narrative - Interim',
        'Narrative Consolidated - Final',
        'Narrative Consolidated - Interim',
        'Thematic Consolidated - Final',
        'Thematic Consolidated - Interim',
        'Thematic Global - Final',
        'Thematic Global - Interim',
        'Thematic - Final',
        'Thematic - Interim',
        'Short Summary Update',
        'Official Receipts',
        'Quarterly Monitoring Report',
    ]

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
            'DRPDonorDocument': ','.join(document_type_filter),
            'DRPModified__gte': modified_date.strftime('%Y-%m-%d')
        }
        serializer_fields = DRPSharePointSearchSerializer._declared_fields.keys()
        selected = ['DRP' + to_camel(x) for x in serializer_fields] + ["Title", "Author", "Path"]

        page = 1
        exit_condition = True
        reports = []

        users = UserRole.objects.filter(donor=donor, notification_period=period).values(
            'user__first_name', 'user__email')

        if users:
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
                context = {'reports': reports, 'donor': donor.name}
                recipients = list(set([str(user['user__email']) for user in users if user['user__email']]))
                send_notification_with_template(recipients, 'notify_donor', context)


@app.task
def notify_gavi_donor(donor_code=settings.GAVI_DONOR_CODE):
    logger.info('Notifing GAVI')
    for group_name in Group.objects.filter(name__startswith='MOU').values_list('name', flat=True):
        notify_gavi_donor_ctn.delay(group_name, donor_code)


@app.task
def notify_gavi_donor_ctn(group_name, donor_code):
    logger.info(f'Notifing GAVI {group_name}')
    donor = Donor.objects.get(code=donor_code)
    client = SharePointClient(url=f'{config.SHAREPOINT_TENANT}/{config.SHAREPOINT_SITE_TYPE}/{config.SHAREPOINT_SITE}')

    notification_periods = [x for x in [
        (UserRole.EVERY_MONTH, today().replace(day=1) - relativedelta(months=1), today().day == 1),
        (UserRole.EVERY_MONDAY, today() - timedelta(7), today().weekday() == 0),
        (UserRole.EVERY_DAY, today() - timedelta(1), True),
    ] if x[2]]

    for period, modified_date, _ in notification_periods:
        filters = {
            'DRPDonorCode': donor_code,
            'DRPModified__gte': modified_date.strftime('%Y-%m-%d'),
            'CTNMOUNumber': group_name,
        }

        def to_drp(source, value):
            prefix = 'CTN' if isinstance(value, (CTNSearchSharePointField, CTNSearchMultiSharePointField)) else 'DRP'
            return prefix + to_camel(source)

        selected = [to_drp(key, value) for key, value in GaviSharePointSearchSerializer._declared_fields.items()]
        selected += ["Title", "Author", "Path"]

        page = 1
        exit_condition = True
        reports = []

        users = UserRole.objects.filter(donor=donor, notification_period=period, group__name=group_name).values(
            'user__first_name', 'user__email')

        if users:
            while exit_condition:
                response, total_rows = client.search(
                    filters=filters,
                    select=selected,
                    source_id=settings.DRP_SOURCE_IDS['gavi'],
                    page=page
                )
                exit_condition = page * SHAREPOINT_PAGE_SIZE < total_rows
                page += 1
                qs = GaviSharePointSearchSerializer(response, many=True)
                reports.extend(qs.data)

            if reports:
                context = {'reports': reports, 'donor': donor.name}
                recipients = list(set([str(user['user__email']) for user in users if user['user__email']]))
                send_notification_with_template(recipients, 'notify_gavi', context)


@app.task
def notify_new_records():
    logger.info('Notify Start')
    for donor_code in Donor.objects.filter(active=True).values_list('code', flat=True):
        if donor_code == settings.GAVI_DONOR_CODE:
            notify_gavi_donor(donor_code)
        else:
            notify_donor.delay(donor_code)
