from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel
from unicef_notification.utils import send_notification_with_template

from donor_reporting_portal.apps.report_metadata.models import Donor


class UserRoleManager(models.Manager):

    def by_permissions(self, perms_name):
        if not isinstance(perms_name, (set, list)):
            perms_name = perms_name,
        for perm_name in perms_name:
            app_label, codename = perm_name.split('.')
            self = self.filter(group__permissions__codename=codename,
                               group__permissions__content_type__app_label=app_label)
        return self

    def get_permissions_by_donor(self, user, donor):
        return self.filter(user=user, donor=donor).values_list(
            'group__permissions__content_type__app_label',
            'group__permissions__codename')


class UserRole(TimeStampedModel):
    """A security role of a User."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='roles', on_delete=models.deletion.CASCADE)
    group = models.ForeignKey(Group, related_name='roles', on_delete=models.deletion.CASCADE)
    donor = models.ForeignKey(Donor, related_name='roles', on_delete=models.deletion.CASCADE)
    # grant = models.ForeignKey(Grant, null=True, blank=True, related_name='grants', on_delete=models.deletion.CASCADE)

    objects = UserRoleManager()

    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        unique_together = (('user', 'group', 'donor'),)
        permissions = (
            ('can_view_all_donors', 'Can views all Donors'),
        )

    def __str__(self):
        return f'{self.user} - {self.group} | {self.donor}'


@receiver(post_save, sender=get_user_model())
def assign_to_unicef_group(instance, created, **kwargs):
    if created:
        context = {'instance': instance, 'home_link': settings.HOST}
        send_notification_with_template(
            [instance.email, ],
            "access_grant_email",
            context,
        )
        if instance.username.endswith('@unicef.org'):
            unicef_group, _ = Group.objects.get_or_create(name='UNICEF User')
            instance.groups.add(unicef_group)
