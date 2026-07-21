from django.contrib import admin
from post_office.admin import AttachmentInline as BaseAttachmentInline, EmailAdmin as BaseEmailAdmin
from post_office.models import Email

from unicef_security.admin import UserAdminPlus

from donor_reporting_portal.apps.core.models import User


@admin.register(User)
class UserAdminPlus(UserAdminPlus):
    pass


class AttachmentInline(BaseAttachmentInline):
    def get_queryset(self, request):
        queryset = super(admin.StackedInline, self).get_queryset(request)
        if self.parent_obj:
            queryset = queryset.filter(email=self.parent_obj)
        return queryset.select_related("attachment")


admin.site.unregister(Email)


@admin.register(Email)
class EmailAdmin(BaseEmailAdmin):
    inlines = [AttachmentInline] + [inline for inline in BaseEmailAdmin.inlines if inline is not BaseAttachmentInline]
