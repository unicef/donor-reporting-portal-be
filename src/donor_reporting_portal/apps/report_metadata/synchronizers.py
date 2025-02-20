import logging
from datetime import datetime

from unicef_realm.models import BusinessArea
from unicef_vision.synchronizers import VisionDataSynchronizer

from .models import Donor, ExternalGrant, Grant, SecondaryDonor, Theme

logger = logging.getLogger(__name__)


def get_date(date_string, data_format="%d-%b-%y"):
    return datetime.strptime(date_string, data_format) if date_string else None


def get_type(record):
    if record["THEMATIC"]:
        return Grant.THEMATIC
    if record["USGOV_FLAG"]:
        return Grant.FFR
    return Grant.STANDARD


class GrantSynchronizer(VisionDataSynchronizer):
    ENDPOINT = "dsgrants"
    GLOBAL_CALL = True
    REQUIRED_KEYS = (
        "DONOR_CODE",
        "DONOR_NAME",
        "GRANT_REF",
    )

    def _convert_records(self, records):
        return records["ROWSET"]["ROW"]

    def _save_records(self, records):
        processed = 0
        filtered_records = self._filter_records(records)
        for partner in filtered_records:
            processed += self._item_save(partner)
        return processed

    def _filter_records(self, records):
        return [rec for rec in records if all(key in rec for key in self.REQUIRED_KEYS)]

    @staticmethod
    def _item_save(record):
        logger.info(f'parsing {record["GRANT_REF"]}')

        donor, _ = Donor.objects.update_or_create(
            code=record["DONOR_CODE"],
            defaults={
                "name": record["DONOR_NAME"],
                "us_gov": bool(record["USGOV_FLAG"]),
            },
        )
        grant_defaults = {
            "year": record["ISSUE_YEAR"],
            "expiry_date": get_date(record["EXPIRY_DATE"]),
            "financial_close_date": get_date(record.get("FINANCIALLY_CLOSE_DATE", None)),
            "description": record["DESCRIPTION"],
            "donor": donor,
            "category": get_type(record),
        }
        grant, _ = Grant.objects.update_or_create(code=record["GRANT_REF"], defaults=grant_defaults)
        if record["THEMATIC"]:
            theme, _ = Theme.objects.get_or_create(name=record["THEMATIC"])
            grant_defaults["theme"] = theme
        if record["EXTERNAL_REF"]:
            external_grant, _ = ExternalGrant.objects.get_or_create(
                code=record["EXTERNAL_REF"], defaults={"donor": donor}
            )

        if record.get("RECIPIENT_OFFICE_CODE", None):
            grant.business_areas.set(BusinessArea.objects.filter(code__in=record["RECIPIENT_OFFICE_CODE"].split("; ")))

        if record.get("SECONDARY_DONOR_CODE", None):
            secondary_donors_codes = record["SECONDARY_DONOR_CODE"].split(";")
            secondary_donors_names = record["SECONDARY_DONOR"].split(";")
            if len(secondary_donors_codes) != len(secondary_donors_names):
                return -1
            for code, name in zip(secondary_donors_codes, secondary_donors_names, strict=True):
                (
                    secondary_donor,
                    _,
                ) = SecondaryDonor.objects.get_or_create(code=code, defaults={"name": name})
                secondary_donor.grants.add(grant)

        return 1
