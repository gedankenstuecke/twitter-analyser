from django.test import TestCase, Client
from django.conf import settings


class AboutTestCase(TestCase):
    """
    Test cases for the about view function.
    """

    def setUp(self):
        """
        Set up the app for following test.
        """
        settings.DEBUG = True
        settings.OH_ACTIVITY_PAGE = 'foobar.com'

    def test_about(self):
        """
        Tests the about view function.
        """
        c = Client()
        response = c.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['section'], 'about')
        self.assertEqual(response.context['oh_proj_page'], 'foobar.com')
        self.assertTemplateUsed(response, 'twitteranalyser/about.html')
