from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common_lib.django.drf.decorators import BlinkMessageRenderer, RawJsonParser
from common_lib.django.drf.filters import StableOrderingFilter
from common_lib.django.drf.pagination import CustomizablePageNumberPagination


class BaseMessageAPIView(GenericViewSet):
    """A base view that provides some common functionality for views that use BlinkMessages rather than Serializers"""

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomizablePageNumberPagination
    filter_backends = [DjangoFilterBackend, StableOrderingFilter]  # allows filtering and ordering
    ordering_fields = []  # pass an `ordering` querystring parameter to set (if not blanked, defaults to all fields)
    # these two settings allow a BlinkMessage class to be used as the serializer
    parser_classes = [RawJsonParser]
    renderer_classes = [BlinkMessageRenderer]

    def get_list(self, request, model_to_message: callable, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            messages = [model_to_message(model).to_dict() for model in page]
            return self.get_paginated_response(messages)

        messages = [model_to_message(model) for model in queryset.all()]
        return Response(messages)

    def get_retrieve(self, request, model_to_message: callable, *args, **kwargs):
        instance = self.get_object()
        return Response(model_to_message(instance))
