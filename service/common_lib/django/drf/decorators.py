from blink_messaging.serialization import BlinkMessage
from rest_framework import renderers, parsers


class RawJsonParser(parsers.BaseParser):
    """
    Parses an incoming message as a raw string, allowing it to be parsed fully within the view.

    Within a view function, access the raw text of the request with request.data, and then parse it with something like:
    ex: request = MyMessageClass.from_json(request.data).validate()

    You can use this for a view by wrapping it with rest_framework.decorators.parser_classes.
    ex: @parser_classes([RawJsonParser])
        class MyView(BaseAPIView)
    """

    media_type = "application/json"

    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        encoding = parser_context.get("encoding", "utf-8")
        request = parser_context.get("request")  # not used, but kept as a reference of what is available from context

        return stream.read().decode(encoding)


class RawJsonRenderer(renderers.BaseRenderer):
    """
    Renders a json response from a json string, without altering it

    This is helpful when you have something other than a DRF serializer creating your JSON, and want your json string
    returned as the response un-altered (such as putting quotes around it).
    """

    media_type = "application/json"
    format = "json"

    def render(self, data, media_type=None, renderer_context=None):
        return data


class BlinkMessageRenderer(renderers.BaseRenderer):
    """
    Renders a BlinkMessage response into JSON

    This allows you to return a BlinkMessage object as the response of a view, and have it be rendered correctly.
    ex: return Response(my_message)

    You can use this for a view by wrapping it with rest_framework.decorators.renderer_classes, or setting the
    renderer_classes property on the view class.
    ex: @renderer_classes([BlinkMessageRenderer])
        class MyView(RxApiView):
    ex: renderer_classes = [RawJsonRenderer]
    """

    media_type = "application/json"
    format = "json"

    def render(self, data: BlinkMessage, media_type=None, renderer_context=None):
        if isinstance(data, BlinkMessage):
            return data.to_json()
        elif type(data) is list and all([isinstance(i, BlinkMessage) for i in data]):
            items = ",".join([i.to_json() for i in data])
            return f"[{items}]"
        else:
            # if this is not a BlinkMessage, default to the standard JSONRenderer
            json_renderer = renderers.JSONRenderer()
            return json_renderer.render(data, media_type, renderer_context)
