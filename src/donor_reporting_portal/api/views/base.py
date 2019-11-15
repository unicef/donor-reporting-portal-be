from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter


class GenericAbstractViewSetMixin:
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
