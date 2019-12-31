from django.contrib import admin

from .models import SharePointLibrary, SharePointSite


@admin.register(SharePointSite)
class SharepointSiteAdmin(admin.ModelAdmin):
    search_fields = ('name', 'url')
    list_display = ('name', 'site_type', 'url')


@admin.register(SharePointLibrary)
class DocumentLibraryAdmin(admin.ModelAdmin):
    search_fields = ('name', 'site')
    list_display = ('name', 'site', 'active', 'require_donor_permission')
