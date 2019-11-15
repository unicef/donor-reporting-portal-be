from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers
from unicef_security.models import BusinessArea

from donor_reporting_portal.api.serializers.metadata import DonorSerializer
from donor_reporting_portal.apps.roles.models import UserRole


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, trim_whitespace=True)
    last_name = serializers.CharField(required=True, trim_whitespace=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserRoleSerializer(serializers.ModelSerializer):
    user_last_login = serializers.ReadOnlyField(source='user.last_login')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')
    group_name = serializers.ReadOnlyField(source='group.name')
    donor_name = serializers.ReadOnlyField(source='donor.name')

    class Meta:
        model = UserRole
        fields = ('id', 'user', 'group', 'donor', 'group_name', 'donor_name',
                  'user_last_login', 'user_email', 'user_first_name', 'user_last_name')


class BusinessAreaSerializer(serializers.ModelSerializer):
    country = serializers.ReadOnlyField(source='country.name')

    class Meta:
        model = BusinessArea
        fields = ('code', 'name', 'long_name', 'region', 'country')


class UserProfileSerializer(UserSerializer):
    donor = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    def get_instance(self, obj):
        unicef_user = obj.groups.filter(name='UNICEF User').first()
        if unicef_user:
            return unicef_user, None
        if UserRole.objects.by_permissions(['report_metadata.view_donor', 'roles.add_userrole']).filter(user=obj):
            instance = UserRole.objects.by_permissions(['report_metadata.view_donor',
                                                        'roles.add_userrole']).filter(user=obj).first()
        else:
            instance = UserRole.objects.by_permissions('report_metadata.view_donor').filter(user=obj).first()

        return getattr(instance, 'group', None), getattr(instance, 'donor', None)

    def get_group(self, obj):
        group, _ = self.get_instance(obj)
        serializer = GroupSerializer(instance=group)
        return serializer.data

    def get_donor(self, obj):
        _, donor = self.get_instance(obj)

        serializer = DonorSerializer(instance=donor)
        return serializer.data

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('pk', 'donor', 'group')

    # donors = serializers.SerializerMethodField()
    # admin_donors = serializers.SerializerMethodField()

    # def get_donors(self, obj):
    #     qs = Donor.objects.all()
    #     if not obj.has_perm('roles.can_view_all_donors'):
    #         roles = UserRole.objects.by_permissions('report_metadata.view_donor').filter(user=obj)
    #         qs = qs.filter(roles__in=roles)
    #     serializer = DonorSerializer(instance=qs, many=True)
    #     return serializer.data
    #
    # def get_admin_donors(self, obj):
    #     roles = UserRole.objects.by_permissions(['report_metadata.view_donor',
    #                                              'roles.add_userrole']).filter(user=obj)
    #     donors = Donor.objects.filter(roles__in=roles)
    #     serializer = DonorSerializer(instance=donors, many=True)
    #     return serializer.data
