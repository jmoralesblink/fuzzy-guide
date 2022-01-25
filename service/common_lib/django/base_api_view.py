from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common_lib.django.drf.filters import StableOrderingFilter
from common_lib.django.drf.pagination import CustomizablePageNumberPagination


class BaseApiView(GenericViewSet):
    """A base view that provides good defaults, and some common functionality for views that use Serializers"""

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomizablePageNumberPagination
    filter_backends = [DjangoFilterBackend, StableOrderingFilter]  # allows filtering and ordering
    ordering_fields = []  # pass an `ordering` querystring parameter to set (if not blanked, defaults to all fields)

    def get_queryset(self):
        """Include select_related and prefetch_related options from the serializer, if available"""
        queryset = super().get_queryset()
        serializer_class = self.get_serializer_class()

        if hasattr(serializer_class, "select_related") and serializer_class.select_related:
            queryset = queryset.select_related(*serializer_class.select_related)
        if hasattr(serializer_class, "prefetch_related") and serializer_class.prefetch_related:
            queryset = queryset.prefetch_related(*serializer_class.prefetch_related)

        return queryset

    def get_list(self, request, *args, **kwargs):
        """Return a list of models from the queryset, using the specified serializer"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_retrieve(self, request, *args, **kwargs):
        """Return a single model, specified from the url path"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
