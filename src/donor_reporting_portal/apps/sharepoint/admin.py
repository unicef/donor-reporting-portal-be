from django.contrib import admin

# from .models import SharePointGroup


# @admin.register(SharePointGroup)
class SharePointGroupAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', )
    filter_horizontal = ('libraries', )
