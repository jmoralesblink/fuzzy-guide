from api.tests.view_test_case import ViewTestCase
from core.models import Widget

GET_RETRIEVE_ENDPOINT = "/api/v1/widgets/{id}/"
GET_LIST_ENDPOINT = "/api/v1/widgets/"
POST_CREATE_ENDPOINT = "api/v1/widgets"


class TestRetrieveWidget(ViewTestCase):
    def test_success(self):
        widget = Widget.objects.create(name="test_widget")

        response = self.authenticated_client.get(GET_RETRIEVE_ENDPOINT.format(id=widget.public_id))
        resp_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data["public_id"], str(widget.public_id))
        self.assertEqual(resp_data["name"], widget.name)

    def test_not_found(self):
        invalid_public_id = "b839b1ab-0bf7-4a57-a421-8a5017de8292"

        response = self.authenticated_client.get(GET_RETRIEVE_ENDPOINT.format(id=invalid_public_id))

        self.assertEqual(response.status_code, 404)


class TestListWidget(ViewTestCase):
    def test_get_success(self):
        widget1 = Widget.objects.create(name="test_widget1")
        widget2 = Widget.objects.create(name="test_widget2")

        response = self.authenticated_client.get(GET_LIST_ENDPOINT)
        resp_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data["count"], 2)

    def test_get_not_found(self):
        # widgets not created
        response = self.authenticated_client.get(GET_LIST_ENDPOINT)
        resp_data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(resp_data["count"], 0)
