from django.contrib import admin

from .models import UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'donor__name', 'secondary_donor__name', )
    list_display = ('user', 'group', 'donor')
    list_filter = ('group', 'donor', 'secondary_donor')
    raw_id_fields = ('user', 'group', 'donor', 'secondary_donor')
