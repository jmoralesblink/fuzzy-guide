from rest_framework import routers

from api.v1.views.widget_view import WidgetView

router = routers.SimpleRouter()

router.register(r"widgets", WidgetView, basename="widgets")

urlpatterns = router.urls
