from django.contrib import admin

from .models import UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    search_fields = ('donor', )
    list_display = ('user', 'group', 'donor')
    list_filter = ('group', 'donor')
