from django.contrib import admin

from .models import UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    search_fields = ('donor', 'secondary_donor', )
    list_display = ('user', 'group', 'donor', )  # 'secondary_donor')
    list_filter = ('group', 'donor', 'secondary_donor')
    raw_id_fields = ('user', 'group', 'donor', 'secondary_donor')
