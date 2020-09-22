from datetime import datetime

from django.conf import settings

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from donor_reporting_portal.apps.report_metadata.models import Grant


def dict_to_json(dictionary, key='code', value='label'):
    return [{key: k, value: v} for k, v in dictionary.items()]


class MetadataStaticAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Return All Static values used for drop-down in the frontend"""

        years = {year: year for year in range(2000, datetime.today().year + 2)}
        report_years = {year: year for year in range(2019, datetime.today().year + 2)}
        grant_issue_years = {year: year for year in range(2018, datetime.today().year + 2)}
        report_type = {
            'quarterly': 'Quarterly',
            'final': 'Final',
            'interim': 'Interim'
        }
        donor_document = {
            'certified_statement_of_account': 'Certified Statement of Account',
            'certified_statement_of_account_EU': 'Certified Statement of Account EU',
            'certified_statement_of_account_JPO': 'Certified Statement of Account JPO',
            'donor_statement_CERF': 'Donor Statement CERF',
            'donor_statement_innovation': 'Donor Statement Innovation',
            'donor_statement_joint_programme': 'Donor Statement Joint Programme',
            'donor_statement_joint_programme PUNO': 'Donor Statement Joint Programme PUNO',
            'donor_statement_JPO_summary': 'Donor Statement JPO Summary',
            'donor_statement_trust_fund': 'Donor Statement Trust Fund',
            'donor_statement_UN': 'Donor Statement UN',
            'donor_statement_UNICEF Hosted Funds': 'Donor Statement UNICEF Hosted Funds',
            'JPO_expenditure_summary': 'JPO Expenditure Summary',
            'MDTF_report': 'MDTF Report',
            'Statement_of_account_thematic_funds': 'Statement of Account Thematic Funds',
            'certified_financial_statement_EC': 'Certified Financial Statement - EC',
            'certified_financial_statement_US_government': 'Certified Financial Statement - US Government',
            'uncertified_financial_statements': 'Uncertified Financial Statements',
            'progress_reports': 'Progress Reports',
            'final_reports': 'Final Reports',
            'inception_reports': 'Inception Reports',
            'thematic_reports': 'Thematic Reports',
            'consolidated_emergency_reports': 'Consolidated Emergency Reports',
            'agreements': 'Agreements',
            'agreement_amendments': 'Agreement Amendments',
            'note_for_the_records': 'Note for the Records',
            'correspondence': 'Correspondence',
            'receipts': 'Receipts',
        }
        donor_reporting_category = {
            'financial_cert': 'Donor Financial Certified',
            'financial_uncert': 'Donor Financial Uncertified',
            'narrative': 'Donor Narrative',
        }
        reporting_group = {code: label for (code, label) in Grant.CATEGORIES}
        recertified = {
            'yes': 'Yes',
            'no': 'No'
        }
        rp_status = {
            'new': 'New',
            'pending_rm': 'Pending Review by Reporting Manager',
            'rejected_rm': 'Rejected by Reporting Manager',
            'approved_rm': 'Approved by Reporting Manager',
            'pending_cp': 'Pending Approval by Comptroller',
            'rejected_cp': 'Rejected by Comptroller',
            'certified_cp': 'Certified by Comptroller',
        }

        return Response(
            {
                'years': dict_to_json(years),
                'report_years': dict_to_json(report_years),
                'grant_issue_years': dict_to_json(grant_issue_years),
                'report_type': dict_to_json(report_type),
                'donor_document': dict_to_json(donor_document),
                'donor_reporting_category': dict_to_json(donor_reporting_category),
                'reporting_group': dict_to_json(reporting_group),
                'recertified': dict_to_json(recertified),
                'rp_status': dict_to_json(rp_status),
                'source_id': settings.DRP_SOURCE_IDS
            },
            status=status.HTTP_200_OK
        )
