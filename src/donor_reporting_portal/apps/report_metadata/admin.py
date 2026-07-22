from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from donor_reporting_portal.apps.roles.tasks import notify_donor, notify_gavi_donor

from .models import Donor, DRPMetadata, ExternalGrant, Grant, Theme
from .tasks import grant_sync


class GrantSyncMixin(ExtraButtonsMixin):
    @button()
    def _sync_grants(self, request):
        grant_sync.delay()
        messages.add_message(request, messages.INFO, "Task for Grant sync has been scheduled")
        return HttpResponseRedirect(reverse("admin:report_metadata_grant_changelist"))


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)


@admin.register(ExternalGrant)
class ExternalGrantAdmin(GrantSyncMixin, admin.ModelAdmin):
    search_fields = ("code", "donor__code")
    list_display = ("code", "donor")


@admin.register(Donor)
class DonorAdmin(GrantSyncMixin, ExtraButtonsMixin, admin.ModelAdmin):
    search_fields = ("name", "code")
    list_display = ("name", "code", "us_gov", "active")
    list_filter = ("us_gov", "active")

    @button(change_form=True)
    def _send_notifications(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj.code == settings.GAVI_DONOR_CODE:
            notify_gavi_donor.delay(obj.code)
        else:
            notify_donor.delay(obj.code)
        messages.add_message(request, messages.INFO, f"Notifications scheduled for {obj.name}")
        return HttpResponseRedirect(reverse("admin:report_metadata_donor_change", args=[object_id]))


@admin.register(Grant)
class GrantAdmin(GrantSyncMixin, admin.ModelAdmin):
    search_fields = ("code",)
    list_display = ("code", "donor", "category", "year")
    list_filter = ("category", "donor", "year")
    filter_horizontal = ("business_areas",)


# @admin.register(SecondaryDonor)
class SecondaryDonorAdmin(GrantSyncMixin, admin.ModelAdmin):
    search_fields = ("name", "code")
    list_display = (
        "name",
        "code",
    )
    raw_id_fields = ("grants",)


@admin.register(DRPMetadata)
class DRPMetadataAdmin(admin.ModelAdmin):
    search_fields = ("description", "code")
    list_display = ("category", "description", "audience")
    list_filter = ("category", "audience")
