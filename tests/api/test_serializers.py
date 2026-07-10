from datetime import datetime
from unittest import mock

from django.test import TestCase, override_settings
from rest_framework import serializers

from donor_reporting_portal.api.serializers.fields import (
    CTNSearchSharePointField,
    DRPSearchMultiSharePointField,
    DRPSearchSharePointField,
    SearchMultiSharePointField,
    SearchSharePointField,
)
from donor_reporting_portal.api.serializers.metadata import DonorSecondaryDonorSerializer
from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSerializerMixin,
    DRPSharePointBaseSerializer,
    DRPSharePointSearchSerializer,
    GaviSharePointSearchSerializer,
    GaviSoaSharePointSearchSerializer,
)
from donor_reporting_portal.api.serializers.userrole import UserSerializer
from factories import DonorFactory, GrantFactory, SecondaryDonorFactory
import pytest


class TestSearchSharePointField(TestCase):
    def test_get_search_property_default(self):
        field = SearchSharePointField(source="report_group")
        assert field.get_search_property() == "ReportGroup"

    def test_get_search_property_custom(self):
        field = SearchSharePointField(source="donor_code", search_property="Donor")
        assert field.get_search_property() == "Donor"

    def test_get_serializer_field_name(self):
        field = SearchSharePointField(source="report_group")
        assert field.get_serializer_field_name() == "ReportGroup"

    def test_get_serializer_field_name_with_prefix(self):
        field = DRPSearchSharePointField(source="report_group")
        assert field.get_serializer_field_name() == "DRPReportGroup"
        field2 = CTNSearchSharePointField(source="number")
        assert field2.get_serializer_field_name() == "CTNNumber"

    def test_get_attribute_found(self):
        field = SearchSharePointField(source="report_group")
        val = field.get_attribute({"ReportGroup": "Grant"})
        assert val == "Grant"

    def test_get_attribute_not_found(self):
        field = SearchSharePointField(source="report_group")
        val = field.get_attribute({})
        assert val == "N/A"

    def test_get_attribute_drp_prefix(self):
        field = DRPSearchSharePointField(source="report_group")
        val = field.get_attribute({"DRPReportGroup": "Grant"})
        assert val == "Grant"

    def test_get_attribute_ctn_prefix(self):
        field = CTNSearchSharePointField(source="number")
        val = field.get_attribute({"CTNNumber": "123"})
        assert val == "123"


class TestSearchMultiSharePointField(TestCase):
    def test_get_attribute_semicolon_separated(self):
        field = SearchMultiSharePointField(source="tags")
        field.source_attrs = ["tags"]
        val = field.get_attribute({"tags": "a;b;c"})
        assert val == ["a", "b", "c"]

    def test_get_attribute_empty(self):
        field = SearchMultiSharePointField(source="tags")
        field.source_attrs = ["tags"]
        val = field.get_attribute({"tags": ""})
        assert val == []

    def test_get_attribute_single(self):
        field = SearchMultiSharePointField(source="tags")
        field.source_attrs = ["tags"]
        val = field.get_attribute({"tags": "hello"})
        assert val == ["hello"]

    def test_get_attribute_not_found(self):
        field = SearchMultiSharePointField(source="tags")
        field.source_attrs = ["tags"]
        val = field.get_attribute({})
        assert val == []


class TestDRPSearchMultiSharePointField(TestCase):
    def test_get_attribute_with_prefix(self):
        field = DRPSearchMultiSharePointField(source="recipient_office")
        field.source_attrs = ["recipient_office"]
        val = field.get_attribute({"DRPRecipientOffice": "NYC;LON"})
        assert val == ["NYC", "LON"]

    def test_get_attribute_not_found(self):
        field = DRPSearchMultiSharePointField(source="recipient_office")
        field.source_attrs = ["recipient_office"]
        val = field.get_attribute({})
        assert val == ["N/A"]


class TestDRPSharePointBaseSerializer(TestCase):
    def test_get_property_name_map_drp(self):
        m = DRPSharePointSearchSerializer.get_property_name_map()
        assert m["donor_code"] == "Donor"
        assert m["grant_number"] == "GrantNumber"
        assert m["title"] == "Title"
        assert m["is_new"] == "IsNew"

    def test_get_property_name_map_gavi(self):
        m = GaviSharePointSearchSerializer.get_property_name_map()
        assert m["donor_code"] == "Donor"
        assert m["number"] == "Number"
        assert m["m_o_u_number"] == "MOUNumber"

    def test_get_property_name_map_soa(self):
        m = GaviSoaSharePointSearchSerializer.get_property_name_map()
        assert m["donor_code"] == "Donor"
        assert m["grant_number"] == "GrantNumber"
        assert m["g_a_v_i_w_b_s"] == "GAVIWBS"

    def test_get_property_name_reverse_drp(self):
        r = DRPSharePointSearchSerializer.get_property_name_reverse()
        assert r["DonorCode"] == "DRPDonorCode"
        assert r["GrantNumber"] == "DRPGrantNumber"
        assert r["ReportGroup"] == "DRPReportGroup"
        assert "Title" not in r

    def test_get_property_name_reverse_gavi(self):
        r = GaviSharePointSearchSerializer.get_property_name_reverse()
        assert r["DonorCode"] == "DRPDonorCode"
        assert r["Number"] == "CTNNumber"
        assert r["MOUNumber"] == "CTNMOUNumber"

    def test_get_property_name_reverse_soa(self):
        r = GaviSoaSharePointSearchSerializer.get_property_name_reverse()
        assert r["GrantNumber"] == "DRPGrantNumber"
        assert r["GAVIWBS"] == "CTNGAVIWBS"

    @mock.patch("donor_reporting_portal.api.serializers.sharepoint.datetime")
    def test_get_is_new_within_days(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 6, 30, 12, 0, 0)
        serializer = DRPSharePointBaseSerializer()
        obj = {"DRPModified": "2026-06-28T10:00:00Z"}
        assert serializer.get_is_new(obj) is True

    @mock.patch("donor_reporting_portal.api.serializers.sharepoint.datetime")
    def test_get_is_new_older(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 6, 30, 12, 0, 0)
        serializer = DRPSharePointBaseSerializer()
        obj = {"DRPModified": "2026-06-01T10:00:00Z"}
        assert serializer.get_is_new(obj) is False

    def test_get_is_new_missing(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {}
        assert serializer.get_is_new(obj) is False

    def test_get_is_new_invalid_date(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {"DRPModified": "not-a-date"}
        assert serializer.get_is_new(obj) is False

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_with_path_and_donor(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {
            "Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/doc.pdf",
            "DRPDonorCode": "I49901",
        }
        url = serializer.get_download_url(obj)
        assert "http://localhost:8000/api/sharepoint/" in url
        assert "doc.pdf/download/" in url
        assert "donor_code=I49901" in url

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_with_semicolon_donor(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {
            "Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/doc.pdf",
            "DRPDonorCode": "I49901;I49902",
        }
        url = serializer.get_download_url(obj)
        assert "http://localhost:8000/api/sharepoint/" in url
        assert "doc.pdf/download/" in url
        assert "donor_code=I49901,I49902" in url

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_without_donor(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {"Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/doc.pdf"}
        url = serializer.get_download_url(obj)
        assert "http://localhost:8000/api/sharepoint/" in url
        assert "doc.pdf/download/" in url
        assert "donor_code" not in url

    def test_get_download_url_without_path(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {}
        url = serializer.get_download_url(obj)
        assert url is None

    def test_get_download_url_keyerror(self):
        serializer = DRPSharePointBaseSerializer()
        obj = mock.MagicMock()
        obj.get.side_effect = KeyError("test")
        url = serializer.get_download_url(obj)
        assert url is None


class TestDRPSerializerMixin(TestCase):
    def test_get_is_new_empty_modified(self):
        serializer = DRPSerializerMixin()
        obj = {}
        assert serializer.get_is_new(obj) is False

    def test_get_is_new_none_modified(self):
        serializer = DRPSerializerMixin()
        obj = {"Modified": None}
        assert serializer.get_is_new(obj) is False


class TestDonorSecondaryDonorSerializer(TestCase):
    def test_get_secondary_donors(self):
        donor = DonorFactory()
        grant = GrantFactory(donor=donor)
        secondary_donor = SecondaryDonorFactory()
        secondary_donor.grants.add(grant)

        serializer = DonorSecondaryDonorSerializer(donor)
        assert "secondary_donors" in serializer.data
        assert len(serializer.data["secondary_donors"]) == 1
        assert serializer.data["secondary_donors"][0]["id"] == secondary_donor.pk


class TestUserSerializerValidateEmail(TestCase):
    def test_validate_email_lowercase(self):
        serializer = UserSerializer()
        result = serializer.validate_email("test@example.com")
        assert result == "test@example.com"

    def test_validate_email_uppercase_raises_error(self):
        serializer = UserSerializer()
        with pytest.raises(serializers.ValidationError):
            serializer.validate_email("Test@Example.com")
