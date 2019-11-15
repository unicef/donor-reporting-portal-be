from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from admin_extra_urls.extras import ExtraUrlMixin, link

from .models import Donor, ExternalGrant, Grant, Theme
from .tasks import grant_sync


class GrantSyncMixin(ExtraUrlMixin):

    @link()
    def _sync_grants(self, request):
        grant_sync.delay()
        messages.add_message(request, messages.INFO, 'Task for Grant sync has been scheduled')
        return HttpResponseRedirect(reverse('admin:report_metadata_grant_changelist'))


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', )


@admin.register(ExternalGrant)
class ExternalGrantAdmin(GrantSyncMixin, admin.ModelAdmin):
    search_fields = ('code', 'donor')
    list_display = ('code', 'donor')


@admin.register(Donor)
class DonorAdmin(GrantSyncMixin, admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'code')


@admin.register(Grant)
class GrantAdmin(GrantSyncMixin, admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('code', 'donor', 'category', 'year')
    list_filter = ('category', 'donor', 'year')
    filter_horizontal = (
        'business_areas',
    )
