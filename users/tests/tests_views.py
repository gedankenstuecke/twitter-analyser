from django.test import TestCase, Client
from django.conf import settings
from users.models import OpenHumansMember


class IndexTestCase(TestCase):
    """
    Test cases for the index view function.
    """

    def setUp(self):
        """
        Set up the app for following test.
        """
        settings.DEBUG = True
        settings.OH_CLIENT_ID = 'foo'
        settings.OH_ACTIVITY_PAGE = 'foobar.com'
        settings.OH_REDIRECT_URI = 'foo.com'
        self.oh_member = OpenHumansMember.create(oh_id='1234567890abcdef',
                                                 access_token='foo',
                                                 refresh_token='bar',
                                                 expires_in=2000)
        self.oh_member.save()
        self.user = self.oh_member.user
        self.user.set_password('foobar')
        self.user.save()

    def test_index(self):
        """
        Tests the index view function.
        """
        c = Client()
        response = c.get('/users/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/index.html')
        self.assertEqual(response.context['client_id'], 'foo')
        self.assertEqual(response.context['oh_proj_page'], 'foobar.com')
        self.assertEqual(response.context['redirect_uri'], 'foo.com')

    def test_index_when_authenticated(self):
        """
        Tests the index view function when authenticated.
        """
        c = Client()
        c.login(username=self.user.username, password='foobar')
        response = c.get('/users/')
        self.assertRedirects(response, '/users/dashboard/',
                             status_code=302, target_status_code=200)


class DeleteTestCase(TestCase):
    """
    Test cases for the delete_account view function.
    """

    def setUp(self):
        """
        Set up the app for following test.
        """
        settings.DEBUG = True
        self.oh_member = OpenHumansMember.create(oh_id='1234567890abcdef',
                                                 access_token='foo',
                                                 refresh_token='bar',
                                                 expires_in=2000)
        self.oh_member.save()
        self.user = self.oh_member.user
        self.user.set_password('foobar')
        self.user.save()

    def test_delete(self):
        """
        Tests the delete_account view function.
        """
        c = Client()
        response = c.get('/users/delete/')
        self.assertRedirects(response, '/',
                             status_code=302, target_status_code=302)

    def test_delete_when_authenticated(self):
        """
        Tests the delete_account view function when authenticated.
        """
        c = Client()
        c.login(username=self.user.username, password='foobar')
        response = c.get('/users/delete/')
        self.assertRedirects(response, '/',
                             status_code=302, target_status_code=302)
        self.assertEqual(
            c.login(username=self.user.username, password='foobar'),
            False)


class DashboardTestCase(TestCase):
    """
    Test cases for the dashboard view function.
    """

    def setUp(self):
        """
        Set up the app for following test.
        """
        settings.DEBUG = True
        settings.OH_ACTIVITY_PAGE = 'foobar.com'
        settings.OH_CLIENT_ID = 'foo'
        self.oh_member = OpenHumansMember.create(oh_id='1234567890abcdef',
                                                 access_token='foo',
                                                 refresh_token='bar',
                                                 expires_in=2000)
        self.oh_member.save()
        self.user = self.oh_member.user
        self.user.set_password('foobar')
        self.user.save()

    def test_dashboard(self):
        """
        Tests the dashboard view function
        """
        c = Client()
        response = c.get('/users/dashboard/')
        self.assertRedirects(response, '/',
                             status_code=302, target_status_code=302)

    def test_dashboard_when_authenticated(self):
        """
        Tests the dashboard view function when authenticated
        """
        c = Client()
        response = c.get('/users/dashboard/')
        c.login(username=self.user.username, password='foobar')
        response = c.get('/users/dashboard/')
        self.assertTemplateUsed(response, 'users/dashboard.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['section'], 'home')
        self.assertEqual(response.context['oh_proj_page'], 'foobar.com')
        self.assertEqual(response.context['oh_member'], self.oh_member)
        self.assertEqual(response.context['has_data'], False)
        self.assertEqual(response.context['client_id'], 'foo')


class AccessSwitchTestCase(TestCase):
    """
    Test cases for the access_switch view function.
    """

    def setUp(self):
        """
        Set up the app for following test.
        """
        settings.DEBUG = True
        self.oh_member = OpenHumansMember.create(oh_id='1234567890abcdef',
                                                 access_token='foo',
                                                 refresh_token='bar',
                                                 expires_in=2000,)
        self.oh_member.save()
        self.user = self.oh_member.user
        self.user.set_password('foobar')
        self.user.save()

    def test_access_switch(self):
        """
        Tests the delete_account view function.
        """
        c = Client()
        response = c.get('/users/access_switch/')
        self.assertRedirects(response, '/users/dashboard/',
                             status_code=302, target_status_code=302)
