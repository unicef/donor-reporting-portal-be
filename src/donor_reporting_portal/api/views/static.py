from datetime import datetime

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
            'Emergency  Consolidated - Interim',
            'Thematic Emergency Global - Final',
            'Thematic Emergency Global - Interim',
            'Emergency - Two Pager',
            'Emergency - Final',
            'Emergency - Interim',
            'Human Interest / Photos',
            'Narrative - Final',
            'Narrative - Interim',
            'Narrative Consolidated - Final',
            'Narrative  Consolidated - Interim',
            'Thematic Consolidated - Final',
            'Thematic Consolidated - Interim',
            'Thematic Global - Final',
            'Thematic Global - Interim',
            'Thematic - Final',
            'Thematic - Interim',
            'Short Summary Update',
            'Agreements',
            'Agreement Amendments',
            'Correspondence',
            'Extensions',
            'Framework Agreements',
            'Framework Agreement Checklist',
            'JPOs',
            'Note for the Records',
            'Official Receipts',
            'Others',
            'Proposals',
            'Payment Request',
            'Input Report - Final',
            'Input Report - Interim',
        ]
        donor_reporting_category = [
            'Donor Narrative',
            'Donor Financial Certified',
            'Grant Master Document',
            'Donor Financial Uncertified',
            'Input Report',
            'Donor Narrative Special',
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
        if not (self.request.user.is_superuser or self.request.user.email.endswith('@unicef.org')):
            donor_reporting_category.remove('Input Report',)
            donor_document = [item for item in donor_document if item not in [
                'Input Report - Final',
                'Input Report - Interim',
                'Correspondence',
                'Others',
                'Note for the Record',
                'Framework Agreement Checklist'
            ]]

        return Response(
            {
                'years': list_to_json(years),
                'report_years': list_to_json(report_years),
                'grant_issue_years': list_to_json(grant_issue_years),
                'report_type': list_to_json(report_type),
                'donor_document': list_to_json(donor_document),
                'donor_reporting_category': list_to_json(donor_reporting_category),
                'recertified': list_to_json(recertified),
                'rp_status': list_to_json(rp_status),
            },
            status=status.HTTP_200_OK
        )
