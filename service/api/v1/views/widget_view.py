import logging

from core.services.widget_service import create_widget
from rest_framework.fields import UUIDField, CharField
from rest_framework.response import Response

from common_lib.django.base_api_view import BaseApiView
from common_lib.django.base_serializer import BaseSerializer
from core.models import Widget

_logger = logging.getLogger(__name__)


class WidgetSerializer(BaseSerializer):
    public_id = UUIDField(read_only=True)
    name = CharField(max_length=32)


class WidgetView(BaseApiView):
    lookup_field = "public_id"
    lookup_url_kwarg = "pk"
    filterset_fields = ["public_id", "name"]
    ordering_fields = ["name"]
    ordering = ["name"]
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer

    def list(self, request):
        return self.get_list(request)

    def retrieve(self, request, pk):
        return self.get_retrieve(request)

    def create(self, request):
        serializer = WidgetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        widget = create_widget(name=serializer.validated_data["name"])
        return Response(self.get_serializer(widget).data)
