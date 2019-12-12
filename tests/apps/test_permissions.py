# from mock import MagicMock
# from tests.perms import user_grant_permissions, user_grant_role_permission

# from donor_reporting_portal.api.permissions import DonorPermission

# def test_donor_permission_ko(request, logged_user, donor):
#     request.user = logged_user
#     view = MagicMock()
#     view.kwargs = {'donor_id': donor.id}
#     assert not DonorPermission().has_permission(request, view)
#
#
# def test_donor_permission_ok_view_all_donor(request, logged_user, donor):
#     with user_grant_permissions(logged_user, permissions=['roles.can_view_all_donors']):
#         request.user = logged_user
#         view = MagicMock()
#         view.kwargs = {'donor_id': donor.id}
#         assert DonorPermission().has_permission(request, view)
#
#
# def test_donor_permission_ok_view_specific_donor(request, logged_user, userrole):
#     with user_grant_role_permission(userrole.user, userrole.donor, permissions=['report_metadata.view_donor']):
#         request.user = userrole.user
#         view = MagicMock()
#         view.kwargs = {'donor_id': userrole.donor.id}
#         assert DonorPermission().has_permission(request, view)
