from django.contrib.auth.models import Group

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from unicef_realm.models import BusinessArea
from unicef_security.models import User

from donor_reporting_portal.api.filters import BusinessAreaFilter, GroupFilter, UserFilter, UserRoleFilter
from donor_reporting_portal.api.serializers.userrole import (
    BusinessAreaSerializer,
    GroupSerializer,
    UserProfileSerializer,
    UserRoleSerializer,
    UserSerializer,
)
from donor_reporting_portal.api.views.base import GenericAbstractViewSetMixin
from donor_reporting_portal.apps.roles.models import UserRole


class GroupViewSet(GenericAbstractViewSetMixin, viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    search_fields = ("name",)
    filterset_class = GroupFilter


class UserViewSet(GenericAbstractViewSetMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    search_fields = ("donor__name", "user__username", "group__name")

    @action(detail=False, methods=["get"])
    def my_profile(self, request, *args, **kwargs):
        object = self.request.user
        serializer = UserProfileSerializer(object)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == "my_profile":
            return [
                IsAuthenticated(),
            ]
        return super().get_permissions()


class UserRoleViewSet(GenericAbstractViewSetMixin, viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    filterset_class = UserRoleFilter
    search_fields = (
        "donor__name",
        "secondary_donor__name",
        "group__name",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    def perform_destroy(self, instance):
        user = instance.user
        super().perform_destroy(instance)
        if not user.user_roles.count():
            user.delete()


class BusinessAreaViewSet(GenericAbstractViewSetMixin, viewsets.ModelViewSet):
    queryset = BusinessArea.objects.all()
    serializer_class = BusinessAreaSerializer
    filterset_class = BusinessAreaFilter
    search_fields = ("code", "name", "long_name")
