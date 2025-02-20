from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel
from unicef_notification.utils import send_notification_with_template

from donor_reporting_portal.apps.report_metadata.models import Donor, SecondaryDonor


class UserRoleManager(models.Manager):
    def by_permissions(self, perms_name):
        qs = self
        if not isinstance(perms_name, set | list):
            perms_name = (perms_name,)
        for perm_name in perms_name:
            app_label, codename = perm_name.split(".")
            qs = self.filter(
                group__permissions__codename=codename,
                group__permissions__content_type__app_label=app_label,
            )
        return qs

    def get_permissions_by_donor(self, user, donor):
        return self.filter(user=user, donor=donor, secondary_donor=None).values_list(
            "group__permissions__content_type__app_label",
            "group__permissions__codename",
        )

    def get_permissions_by_donor_secondary_donor(self, user, donor, secondary_donor):
        return self.filter(user=user, donor=donor, secondary_donor=secondary_donor).values_list(
            "group__permissions__content_type__app_label",
            "group__permissions__codename",
        )


class UserRole(TimeStampedModel):
    DISABLED = "none"
    EVERY_DAY = "every_day"
    EVERY_MONDAY = "every_monday"
    EVERY_MONTH = "every_month"

    PERIODS = (
        (DISABLED, "Disabled"),
        (EVERY_DAY, "Every Day"),
        (EVERY_MONDAY, "Every Monday"),
        (EVERY_MONTH, "Every Month"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="user_roles",
        on_delete=models.deletion.CASCADE,
    )
    group = models.ForeignKey(Group, related_name="user_roles", on_delete=models.deletion.CASCADE)
    donor = models.ForeignKey(Donor, related_name="user_roles", on_delete=models.deletion.CASCADE)
    secondary_donor = models.ForeignKey(
        SecondaryDonor,
        null=True,
        blank=True,
        default=None,
        related_name="user_roles",
        on_delete=models.deletion.CASCADE,
    )
    notification_period = models.CharField(
        max_length=16,
        choices=PERIODS,
        default=DISABLED,
        verbose_name=_("Notification Period"),
    )
    objects = UserRoleManager()

    class Meta:
        verbose_name = _("User Role")
        verbose_name_plural = _("User Roles")
        unique_together = (("user", "group", "donor", "secondary_donor"),)
        permissions = (
            ("can_view_all_donors", "Can views all Donors"),
            ("is_unicef_user", "Is UNICEF User"),
        )

    def __str__(self):
        desc = f"{self.user} - {self.group} | {self.donor}"
        if self.secondary_donor:
            desc = f"{desc} | {self.secondary_donor}"
        return desc


@receiver(post_save, sender=get_user_model())
def assign_to_unicef_group(instance, created, **kwargs):
    if created and instance.email:
        if instance.username.endswith("@unicef.org"):
            unicef_group, _ = Group.objects.get_or_create(name="UNICEF User")
            instance.groups.add(unicef_group)
        else:
            context = {"instance": instance, "home_link": settings.HOST}
            send_notification_with_template(
                [
                    instance.email,
                ],
                "access_grant_email",
                context,
            )
