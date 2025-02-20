from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers
from unicef_realm.models import BusinessArea

from donor_reporting_portal.api.serializers.metadata import DonorSerializer, SecondaryDonorSerializer
from donor_reporting_portal.apps.roles.models import UserRole


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, trim_whitespace=True)
    last_name = serializers.CharField(required=True, trim_whitespace=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "email", "is_superuser")

    def validate_email(self, value):
        if value != value.lower():
            raise serializers.ValidationError("The email should be lowercase")
        return value


class UserRoleSerializer(serializers.ModelSerializer):
    user_last_login = serializers.ReadOnlyField(source="user.last_login")
    user_email = serializers.ReadOnlyField(source="user.email")
    user_first_name = serializers.ReadOnlyField(source="user.first_name")
    user_last_name = serializers.ReadOnlyField(source="user.last_name")
    group_name = serializers.ReadOnlyField(source="group.name")
    donor_name = serializers.ReadOnlyField(source="donor.name")
    secondary_donor_name = serializers.ReadOnlyField(source="secondary_donor.name")

    class Meta:
        model = UserRole
        fields = (
            "id",
            "user",
            "group",
            "donor",
            "secondary_donor",
            "group_name",
            "donor_name",
            "secondary_donor_name",
            "notification_period",
            "user_last_login",
            "user_email",
            "user_first_name",
            "user_last_name",
        )


class BusinessAreaSerializer(serializers.ModelSerializer):
    country = serializers.ReadOnlyField(source="country.name")

    class Meta:
        model = BusinessArea
        fields = ("code", "name", "long_name", "region", "country")


class UserProfileSerializer(UserSerializer):
    donor = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    secondary_donor = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    is_unicef_user = serializers.SerializerMethodField()

    def get_is_unicef_user(self, obj):
        unicef_user = obj.groups.filter(name="UNICEF User").first()
        return bool(unicef_user)

    def get_roles(self, obj):
        qs = UserRole.objects.by_permissions(
            [
                "report_metadata.view_donor",
            ]
        ).filter(user=obj)
        return UserRoleSerializer(qs, many=True).data

    def get_instance(self, obj):
        if UserRole.objects.by_permissions(["report_metadata.view_donor", "roles.add_userrole"]).filter(user=obj):
            instance = (
                UserRole.objects.by_permissions(["report_metadata.view_donor", "roles.add_userrole"])
                .filter(user=obj)
                .first()
            )
        else:
            instance = UserRole.objects.by_permissions("report_metadata.view_donor").filter(user=obj).first()

        return (
            getattr(instance, "group", None),
            getattr(instance, "donor", None),
            getattr(instance, "secondary_donor", None),
        )

    def get_group(self, obj):
        group, _, _ = self.get_instance(obj)
        serializer = GroupSerializer(instance=group)
        return serializer.data

    def get_donor(self, obj):
        _, donor, _ = self.get_instance(obj)

        serializer = DonorSerializer(instance=donor)
        return serializer.data

    def get_secondary_donor(self, obj):
        _, _, secondary_donor = self.get_instance(obj)

        serializer = SecondaryDonorSerializer(instance=secondary_donor)
        return serializer.data

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "is_unicef_user",
            "pk",
            "donor",
            "group",
            "secondary_donor",
            "roles",
        )
