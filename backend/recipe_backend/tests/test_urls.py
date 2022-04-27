from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Get a home page."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)
