import datetime
from datetime import timedelta
from unittest import mock

import pytest
from django.conf import settings
from django.utils.timezone import now

from donor_reporting_portal.apps.roles.models import UserRole
from donor_reporting_portal.apps.roles.tasks import (
    DonorNotifier,
    GaviNotifier,
    GaviUrgentNotifier,
    Notifier,
    notify_donor,
    notify_gavi_donor,
    notify_gavi_donor_ctn,
    notify_new_records,
    notify_urgent_by_group,
    notify_urgent_records,
)
from factories import DonorFactory, GroupFactory, UserRoleFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Notifier (base class)
# ---------------------------------------------------------------------------


FIXED_TODAY = datetime.datetime(2026, 6, 3, 12, 0, 0)  # Wednesday, not day 1


class TestNotifier:
    def test_init(self):
        donor = DonorFactory(name="Donor A")
        notifier = Notifier(donor.code)
        assert notifier.donor == donor

    def test_init_raises_when_donor_missing(self):
        with pytest.raises(DonorFactory._meta.model.DoesNotExist):
            Notifier("__nonexistent__")

    def test_get_notify_periods_all(self):
        """Day 1 and Monday -> EVERY_MONTH + EVERY_MONDAY + EVERY_DAY."""
        # June 1, 2026 is a Monday
        dt = datetime.datetime(2026, 6, 1, 12, 0, 0)
        donor = DonorFactory(name="D")
        with mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=dt):
            periods = Notifier(donor.code).get_notify_periods()
        assert len(periods) == 3
        assert periods[0][0] == UserRole.EVERY_MONTH
        assert periods[1][0] == UserRole.EVERY_MONDAY
        assert periods[2][0] == UserRole.EVERY_DAY

    def test_get_notify_periods_monday_only(self):
        """Monday but not day 1 -> EVERY_MONDAY + EVERY_DAY."""
        # June 8, 2026 is a Monday
        dt = datetime.datetime(2026, 6, 8, 12, 0, 0)
        donor = DonorFactory(name="D")
        with mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=dt):
            periods = Notifier(donor.code).get_notify_periods()
        assert len(periods) == 2
        assert periods[0][0] == UserRole.EVERY_MONDAY
        assert periods[1][0] == UserRole.EVERY_DAY

    def test_get_notify_periods_other_day(self):
        """Neither day 1 nor Monday -> EVERY_DAY only."""
        # June 3, 2026 is a Wednesday
        dt = datetime.datetime(2026, 6, 3, 12, 0, 0)
        donor = DonorFactory(name="D")
        with mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=dt):
            periods = Notifier(donor.code).get_notify_periods()
        assert len(periods) == 1
        assert periods[0][0] == UserRole.EVERY_DAY

    def test_get_filter_dict(self):
        notifier = Notifier(DonorFactory(name="D").code)
        assert notifier.get_filter_dict(mock.Mock()) == {}

    def test_get_searchable_properties(self):
        notifier = Notifier(DonorFactory(name="D").code)
        assert notifier.get_searchable_properties() == set()

    def test_get_reverse_map_no_serializer(self):
        notifier = Notifier(DonorFactory(name="D").code)
        assert notifier.serializer is None
        assert notifier.get_reverse_map() is None

    def test_get_reverse_map_with_serializer(self):
        notifier = Notifier(DonorFactory(name="D").code)
        fake_serializer = mock.MagicMock()
        fake_serializer.get_property_name_reverse.return_value = {"Mapped": "Original"}
        notifier.serializer = fake_serializer
        assert notifier.get_reverse_map() == {"Mapped": "Original"}
        fake_serializer.get_property_name_reverse.assert_called_once_with()

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("Donor", "Donor"),
            ("Modified__gte", "RefinableDate11__gte"),
            ("-Modified", "-RefinableDate11"),
            ("-Modified__gte", "-RefinableDate11__gte"),
            ("Unknown", "Unknown"),
            ("Unknown__suffix", "Unknown__suffix"),
            ("-Unknown__suffix", "-Unknown__suffix"),
        ],
    )
    def test_map_name_to_managed(self, name, expected):
        assert Notifier._map_name_to_managed(name) == expected

    # -- notify() -----------------------------------------------------------

    def test_notify_no_users(self):
        """No users -> notification is not sent."""
        donor = DonorFactory(name="D", code="C1")
        n = Notifier(donor.code)
        n.template_name = "t"
        n.get_queryset = mock.MagicMock(return_value=[])
        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.GraphClient") as gc,
            mock.patch("donor_reporting_portal.apps.roles.tasks.send_notification_with_template") as send,
            mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=FIXED_TODAY),
        ):
            n.notify()
        gc.assert_called_once()
        send.assert_not_called()

    def test_notify_happy_path(self):
        """Full flow with one page of results."""
        donor = DonorFactory(name="Test Donor", code="C1")
        n = Notifier(donor.code)
        n.template_name = "my_template"
        n.group_name = "My Group"
        n.page_size = 500

        n.get_queryset = mock.MagicMock(
            return_value=[
                {"user__email": "a@b.com", "user__first_name": "A"},
            ]
        )
        n.get_filter_dict = mock.MagicMock(return_value={"Donor": "C1"})
        n.get_searchable_properties = mock.MagicMock(return_value={"Donor"})
        n.get_reverse_map = mock.MagicMock(return_value=None)

        mock_client = mock.MagicMock()
        mock_client.search.return_value = ([{"Donor": "C1"}], 1)

        mock_ser_data = mock.MagicMock()
        mock_ser_data.data = [{"DRPModified": "2026-01-01"}]

        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.GraphClient", return_value=mock_client),
            mock.patch("donor_reporting_portal.apps.roles.tasks.send_notification_with_template") as send,
            mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=FIXED_TODAY),
        ):
            n.serializer = mock.MagicMock(return_value=mock_ser_data)
            n.notify()

        mock_client.search.assert_called_once()
        send.assert_called_once_with(
            ["a@b.com"],
            "my_template",
            {"reports": [{"DRPModified": "2026-01-01"}], "donor": "Test Donor", "group_name": "My Group"},
        )

    def test_notify_pagination(self):
        """Multiple pages are fetched until all rows are consumed."""
        donor = DonorFactory(name="D")
        n = Notifier(donor.code)
        n.template_name = "t"
        n.page_size = 2

        n.get_queryset = mock.MagicMock(return_value=[{"user__email": "a@b.com", "user__first_name": "A"}])
        n.get_filter_dict = mock.MagicMock(return_value={})
        n.get_searchable_properties = mock.MagicMock(return_value=set())
        n.get_reverse_map = mock.MagicMock(return_value=None)

        mock_client = mock.MagicMock()
        # page=1 returns 2 items, total_rows=5 -> continue
        # page=2 returns 2 items, total_rows=5 -> continue
        # page=3 returns 1 item,  total_rows=5 -> stop (5 <= 3*2)
        mock_client.search.side_effect = [
            ([{"x": 1}, {"x": 2}], 5),
            ([{"x": 3}, {"x": 4}], 5),
            ([{"x": 5}], 5),
        ]

        mock_ser = mock.MagicMock()
        mock_ser.data = [{"DRPModified": "2026-01-01"}]
        mock_ser_cls = mock.MagicMock(return_value=mock_ser)

        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.GraphClient", return_value=mock_client),
            mock.patch("donor_reporting_portal.apps.roles.tasks.send_notification_with_template"),
            mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=FIXED_TODAY),
        ):
            n.serializer = mock_ser_cls
            n.notify()

        assert mock_client.search.call_count == 3

    def test_notify_zero_total_rows(self):
        """total_rows = 0 -> notification is not sent."""
        donor = DonorFactory(name="D")
        n = Notifier(donor.code)
        n.template_name = "t"

        n.get_queryset = mock.MagicMock(return_value=[{"user__email": "a@b.com", "user__first_name": "A"}])
        n.get_filter_dict = mock.MagicMock(return_value={})
        n.get_searchable_properties = mock.MagicMock(return_value=set())
        n.get_reverse_map = mock.MagicMock(return_value=None)

        mock_client = mock.MagicMock()
        mock_client.search.return_value = ([], 0)

        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.GraphClient", return_value=mock_client),
            mock.patch("donor_reporting_portal.apps.roles.tasks.send_notification_with_template") as send,
            mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=FIXED_TODAY),
        ):
            n.serializer = mock.MagicMock()
            n.notify()

        send.assert_not_called()

    def test_notify_deduplicates_recipients(self):
        """Duplicate and empty emails are handled correctly."""
        donor = DonorFactory(name="D")
        n = Notifier(donor.code)
        n.template_name = "t"
        n.page_size = 500

        n.get_queryset = mock.MagicMock(
            return_value=[
                {"user__email": "dup@x.com", "user__first_name": "A"},
                {"user__email": "dup@x.com", "user__first_name": "B"},
                {"user__email": "", "user__first_name": "C"},
                {"user__email": None, "user__first_name": "D"},
                {"user__email": "unique@x.com", "user__first_name": "E"},
            ]
        )
        n.get_filter_dict = mock.MagicMock(return_value={})
        n.get_searchable_properties = mock.MagicMock(return_value=set())
        n.get_reverse_map = mock.MagicMock(return_value=None)

        mock_client = mock.MagicMock()
        mock_client.search.return_value = ([{"x": 1}], 1)

        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.GraphClient", return_value=mock_client),
            mock.patch("donor_reporting_portal.apps.roles.tasks.send_notification_with_template") as send,
            mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=FIXED_TODAY),
        ):
            n.serializer = mock.MagicMock(return_value=mock.MagicMock(data=[{"DRPModified": "2026-01-01"}]))
            n.notify()

        recipients = send.call_args[0][0]
        assert sorted(recipients) == sorted(["dup@x.com", "unique@x.com"])

    def test_notify_sorts_reports_descending(self):
        """reports.sort(key=lambda r: r.get('DRPModified', '') or '', reverse=True)."""
        donor = DonorFactory(name="D")
        n = Notifier(donor.code)
        n.template_name = "t"
        n.page_size = 500

        n.get_queryset = mock.MagicMock(return_value=[{"user__email": "a@b.com", "user__first_name": "A"}])
        n.get_filter_dict = mock.MagicMock(return_value={})
        n.get_searchable_properties = mock.MagicMock(return_value=set())
        n.get_reverse_map = mock.MagicMock(return_value=None)

        mock_client = mock.MagicMock()
        mock_client.search.return_value = ([{"x": 1}], 3)

        mock_ser = mock.MagicMock()
        mock_ser.data = [
            {"DRPModified": "2026-01-03"},
            {"DRPModified": "2026-01-01"},
            {"DRPModified": "2026-01-02"},
        ]

        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.GraphClient", return_value=mock_client),
            mock.patch("donor_reporting_portal.apps.roles.tasks.send_notification_with_template") as send,
            mock.patch("donor_reporting_portal.apps.roles.tasks.today", return_value=FIXED_TODAY),
        ):
            n.serializer = mock.MagicMock(return_value=mock_ser)
            n.notify()

        sent_reports = send.call_args[0][2]["reports"]
        dates = [r["DRPModified"] for r in sent_reports]
        assert dates == ["2026-01-03", "2026-01-02", "2026-01-01"]


# ---------------------------------------------------------------------------
# DonorNotifier
# ---------------------------------------------------------------------------


class TestDonorNotifier:
    def test_serializer_and_template(self):
        assert DonorNotifier.serializer is not None
        assert DonorNotifier.template_name == "notify_donor"

    def test_get_filter_dict(self):
        donor = DonorFactory(name="D", code="C001")
        n = DonorNotifier(donor.code)
        modified_date = datetime.datetime(2026, 3, 15, 10, 0, 0)
        result = n.get_filter_dict(modified_date)
        assert result["Donor"] == "C001"
        assert "Certified Financial Statement" in result["DonorDocument"]
        assert result["Modified__gte"] == "2026-03-15"

    def test_get_searchable_properties(self):
        n = DonorNotifier(DonorFactory(name="D").code)
        assert n.get_searchable_properties() == {"Donor", "DonorDocument", "Modified"}

    def test_get_queryset(self):
        donor = DonorFactory(name="D")
        group = GroupFactory(name="G")
        user_role = UserRoleFactory(
            donor=donor,
            group=group,
            notification_period=UserRole.EVERY_DAY,
        )
        n = DonorNotifier(donor.code)
        qs = n.get_queryset(UserRole.EVERY_DAY)
        assert len(qs) == 1
        assert qs[0]["user__email"] == user_role.user.email

    def test_get_queryset_filters_by_period(self):
        donor = DonorFactory(name="D")
        group = GroupFactory(name="G")
        UserRoleFactory(
            donor=donor,
            group=group,
            notification_period=UserRole.EVERY_MONTH,
        )
        n = DonorNotifier(donor.code)
        qs = n.get_queryset(UserRole.EVERY_DAY)
        assert len(qs) == 0


# ---------------------------------------------------------------------------
# GaviNotifier
# ---------------------------------------------------------------------------


class TestGaviNotifier:
    def test_init_sets_group_name_and_specific_date(self):
        donor = DonorFactory(name="GAVI", code="G001")
        n = GaviNotifier(donor.code, "MOU-Alpha", specific_date="2026-05-01")
        assert n.group_name == "MOU-Alpha"
        assert n.specific_date == "2026-05-01"
        assert n.donor == donor

    def test_init_specific_date_defaults_to_none(self):
        donor = DonorFactory(name="GAVI", code="G001")
        n = GaviNotifier(donor.code, "MOU-Beta")
        assert n.specific_date is None

    def test_serializer_and_template(self):
        assert GaviNotifier.serializer is not None
        assert GaviNotifier.template_name == "notify_gavi"

    def test_get_queryset(self):
        donor = DonorFactory(name="GAVI", code="G001")
        group = GroupFactory(name="MOU-Alpha")
        ur = UserRoleFactory(
            donor=donor,
            group=group,
            notification_period=UserRole.EVERY_DAY,
        )
        # Another UserRole in a different group should not appear
        other_group = GroupFactory(name="MOU-Beta")
        UserRoleFactory(
            donor=donor,
            group=other_group,
            notification_period=UserRole.EVERY_DAY,
        )
        n = GaviNotifier(donor.code, "MOU-Alpha")
        qs = n.get_queryset(UserRole.EVERY_DAY)
        assert len(qs) == 1
        assert qs[0]["user__email"] == ur.user.email

    def test_get_filter_dict_uses_specific_date(self):
        donor = DonorFactory(name="GAVI", code="G001")
        n = GaviNotifier(donor.code, "MOU-X", specific_date="2026-07-01")
        result = n.get_filter_dict(mock.Mock())
        assert result["Modified"] == "2026-07-01"
        assert result["MOUReference"] == "MOU-X"
        assert result["Urgent__not"] == "Yes"

    def test_get_filter_dict_falls_back_to_modified_date(self):
        donor = DonorFactory(name="GAVI", code="G001")
        n = GaviNotifier(donor.code, "MOU-X")
        modified_date = datetime.datetime(2026, 8, 15, 12, 0, 0)
        result = n.get_filter_dict(modified_date)
        assert result["Modified"] == "2026-08-15"

    def test_get_searchable_properties(self):
        n = GaviNotifier(DonorFactory(name="GAVI").code, "MOU-X")
        assert n.get_searchable_properties() == {"Modified", "MOUReference", "Urgent"}


# ---------------------------------------------------------------------------
# GaviUrgentNotifier
# ---------------------------------------------------------------------------


class TestGaviUrgentNotifier:
    def test_template_name(self):
        assert GaviUrgentNotifier.template_name == "notify_urgent_gavi"

    def test_get_notify_periods(self):
        donor = DonorFactory(name="GAVI")
        n = GaviUrgentNotifier(donor.code, "MOU-X")
        periods = n.get_notify_periods()
        assert len(periods) == 1
        period_name, modified_date, condition = periods[0]
        assert period_name == UserRole.EVERY_DAY
        assert isinstance(modified_date, type(now() - timedelta(seconds=3600)))
        assert condition is True

    def test_get_filter_dict(self):
        donor = DonorFactory(name="GAVI")
        n = GaviUrgentNotifier(donor.code, "MOU-X")
        modified_date = datetime.datetime(2026, 9, 1, 14, 30, 0)
        result = n.get_filter_dict(modified_date)
        assert result["Modified__gte"] == "2026-09-01T14:30:00Z"
        assert result["MOUReference"] == "MOU-X"
        assert result["Urgent"] == "Yes"

    def test_get_searchable_properties(self):
        n = GaviUrgentNotifier(DonorFactory(name="GAVI").code, "MOU-X")
        assert n.get_searchable_properties() == {"Modified", "MOUReference", "Urgent"}


# ---------------------------------------------------------------------------
# Celery tasks
# ---------------------------------------------------------------------------


class TestNotifyDonorTask:
    def test_creates_notifier_and_calls_notify(self):
        DonorFactory(name="D", code="C1")
        with mock.patch("donor_reporting_portal.apps.roles.tasks.DonorNotifier") as mock_notifier_cls:
            instance = mock_notifier_cls.return_value
            notify_donor("C1")
        mock_notifier_cls.assert_called_once_with("C1")
        instance.notify.assert_called_once_with()


class TestNotifyGaviDonorTask:
    def test_iterates_mou_groups_and_dispatches_ctn(self):
        GroupFactory(name="MOU-Alpha")
        GroupFactory(name="MOU-Beta")
        GroupFactory(name="Other")  # should be ignored

        donor_code = settings.GAVI_DONOR_CODE
        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.time.sleep") as mock_sleep,
            mock.patch("donor_reporting_portal.apps.roles.tasks.notify_gavi_donor_ctn.delay") as mock_delay,
        ):
            notify_gavi_donor(donor_code, specific_date="2026-06-01")

        assert mock_delay.call_count == 2
        mock_delay.assert_any_call(donor_code, "MOU-Alpha", "2026-06-01")
        mock_delay.assert_any_call(donor_code, "MOU-Beta", "2026-06-01")
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(5)


class TestNotifyGaviDonorCtnTask:
    def test_creates_gavi_notifier_and_calls_notify(self):
        donor = DonorFactory(name="GAVI", code=settings.GAVI_DONOR_CODE)
        with mock.patch("donor_reporting_portal.apps.roles.tasks.GaviNotifier") as mock_notifier_cls:
            instance = mock_notifier_cls.return_value
            notify_gavi_donor_ctn(donor.code, "MOU-X", specific_date="2026-06-01")

        mock_notifier_cls.assert_called_once_with(donor.code, "MOU-X", specific_date="2026-06-01")
        instance.notify.assert_called_once_with()

    def test_specific_date_defaults_to_none(self):
        donor = DonorFactory(name="GAVI", code=settings.GAVI_DONOR_CODE)
        with mock.patch("donor_reporting_portal.apps.roles.tasks.GaviNotifier") as mock_notifier_cls:
            notify_gavi_donor_ctn(donor.code, "MOU-X")
        mock_notifier_cls.assert_called_once_with(donor.code, "MOU-X", specific_date=None)


class TestNotifyNewRecordsTask:
    def test_dispatches_gavi_and_other_donors(self):
        DonorFactory(name="UNICEF A", code="DA01", active=True)
        DonorFactory(name="UNICEF B", code="DA02", active=True)
        DonorFactory(name="Inactive", code="DA03", active=False)
        gavi_donor = DonorFactory(name="GAVI", code=settings.GAVI_DONOR_CODE, active=True)

        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.notify_donor.delay") as mock_donor_delay,
            mock.patch("donor_reporting_portal.apps.roles.tasks.notify_gavi_donor.delay") as mock_gavi_delay,
        ):
            notify_new_records()

        mock_donor_delay.assert_any_call("DA01")
        mock_donor_delay.assert_any_call("DA02")
        mock_gavi_delay.assert_called_once_with(gavi_donor.code)
        assert mock_donor_delay.call_count == 2

    def test_no_active_donors(self):
        DonorFactory(name="Inactive", code="DA01", active=False)
        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.notify_donor.delay") as mock_donor_delay,
            mock.patch("donor_reporting_portal.apps.roles.tasks.notify_gavi_donor.delay") as mock_gavi_delay,
        ):
            notify_new_records()
        mock_donor_delay.assert_not_called()
        mock_gavi_delay.assert_not_called()


class TestNotifyUrgentByGroupTask:
    def test_creates_gavi_urgent_notifier_and_calls_notify(self):
        DonorFactory(name="GAVI", code=settings.GAVI_DONOR_CODE)
        with mock.patch("donor_reporting_portal.apps.roles.tasks.GaviUrgentNotifier") as mock_notifier_cls:
            instance = mock_notifier_cls.return_value
            notify_urgent_by_group("MOU-X")
        mock_notifier_cls.assert_called_once_with(settings.GAVI_DONOR_CODE, "MOU-X")
        instance.notify.assert_called_once_with()


class TestNotifyUrgentRecordsTask:
    def test_iterates_mou_groups_and_dispatches(self):
        GroupFactory(name="MOU-Alpha")
        GroupFactory(name="MOU-Beta")
        GroupFactory(name="NotMOU")

        with (
            mock.patch("donor_reporting_portal.apps.roles.tasks.time.sleep") as mock_sleep,
            mock.patch("donor_reporting_portal.apps.roles.tasks.notify_urgent_by_group.delay") as mock_delay,
        ):
            notify_urgent_records()

        assert mock_delay.call_count == 2
        mock_delay.assert_any_call("MOU-Alpha")
        mock_delay.assert_any_call("MOU-Beta")
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(5)

    def test_no_mou_groups(self):
        GroupFactory(name="Alpha")
        GroupFactory(name="Beta")
        with mock.patch("donor_reporting_portal.apps.roles.tasks.notify_urgent_by_group.delay") as mock_delay:
            notify_urgent_records()
        mock_delay.assert_not_called()
