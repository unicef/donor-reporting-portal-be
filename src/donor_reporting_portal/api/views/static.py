from datetime import datetime

from django.conf import settings

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


def list_to_json(items, key='code', value='label'):
    return [{key: x.lower().replace(' ', '_'), value: x} for x in items]


class MetadataStaticAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Return All Static values used for drop-down in the frontend"""

        years = [str(year) for year in range(2000, datetime.today().year + 2)]
        report_years = [str(year) for year in range(2019, datetime.today().year + 2)]
        grant_issue_years = [str(year) for year in range(2018, datetime.today().year + 2)]
        report_type = [
            'Quarterly',
            'Final',
            'Interim'
        ]
        donor_document = [
            'Certified Statement of Account',
            'Certified Statement of Account EU',
            'Certified Statement of Account JPO',
            'Donor Statement CERF',
            'Donor Statement Innovation',
            'Donor Statement Joint Programme',
            'Donor Statement Joint Programme PUNO',
            'Donor Statement JPO Summary',
            'Donor Statement Trust Fund',
            'Donor Statement UN',
            'Donor Statement UNICEF Hosted Funds',
            'JPO Expenditure Summary',
            'MDTF Report',
            'Statement of Account Thematic Funds',
            'Certified Financial Statement - EC',
            'Certified Financial Statement - US Government',
            'Uncertified Financial Statements',
            'Progress Reports',
            'Final Reports',
            'Inception Reports',
            'Thematic Reports',
            'Consolidated Emergency Reports',
            'Agreements',
            'Agreement Amendments',
            'Note for the Records',
            'Correspondence',
            'Receipts',
        ]
        donor_reporting_category = [
            'Donor Financial Certified',
            'Donor Financial Uncertified',
            'Donor Narrative',
            'Special Donor Narrative',
            'Special Grant Master',
            'Input Report'
        ]
        reporting_group = [
            'Certified Financial Report - Final',
            'Certified Financial Report - Interim',
            'Certified Financial Statement - EC',
            'Certified Financial Statement - US Government',
            'Certified Statement of Account',
            'Certified Statement of Account EU',
            'Certified Statement of Account JPO',
            'Donor Statement CERF',
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
            'Funds Request Report',
            'Interim Statement by Nature of expense',
            'Non-Standard Statement',
            'Emergency  Consolidated - Interim',
            'Emergency - Final',
            'Emergency - Interim',
            'Emergency - Two Pager',
            'Emergency Consolidated - Final',
            'Human Interest / Photos',
            'Narrative  Consolidated - Interim',
            'Narrative - Final',
            'Narrative - Interim',
            'Narrative Consolidated - Final',
            'Thematic - Final',
            'Thematic - Interim',
            'Thematic Consolidated - Final',
            'Thematic Consolidated - Interim',
            'Thematic Emergency Global - Final',
            'Thematic Emergency Global - Interim',
            'Thematic Global - Final',
            'Thematic Global - Interim',
            'Short Summary Update',
            'Human Interest Stories or Photos',
            'Agreement Amendments',
            'Agreements',
            'Correspondence',
            'Extensions',
            'Framework Agreement Checklist',
            'Framework Agreements',
            'JPOs',
            'Note for the Records',
            'Official Receipts',
            'Others',
            'Payment Request',
            'Proposals',
            'Input Report - Final',
            'Input Report - Interim',
        ]
        recertified = {
            'yes': 'Yes',
            'no': 'No'
        }
        rp_status = [
            'New',
            'Pending Review by Reporting Manager',
            'Rejected by Reporting Manager',
            'Approved by Reporting Manager',
            'Pending Approval by Comptroller',
            'Rejected by Comptroller',
            'Certified by Comptroller',
        ]

        return Response(
            {
                'years': list_to_json(years),
                'report_years': list_to_json(report_years),
                'grant_issue_years': list_to_json(grant_issue_years),
                'report_type': list_to_json(report_type),
                'donor_document': list_to_json(donor_document),
                'donor_reporting_category': list_to_json(donor_reporting_category),
                'reporting_group': list_to_json(reporting_group),
                'recertified': list_to_json(recertified),
                'rp_status': list_to_json(rp_status),
                'source_id': settings.DRP_SOURCE_IDS
            },
            status=status.HTTP_200_OK
        )
