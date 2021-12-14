from django.contrib import admin
from django.contrib.admin import site

from adminactions import actions

from .models import UserRole

actions.add_to_site(site)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'donor__name', 'secondary_donor__name', )
    list_display = ('user', 'group', 'donor')
    list_filter = ('group', 'donor', 'secondary_donor', 'notification_period')
    raw_id_fields = ('user', 'group', 'donor', 'secondary_donor')
