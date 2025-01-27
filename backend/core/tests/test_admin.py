"""
Test suit for the Django Admin modifications.
"""

from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model


class AdminPanelTests(TestCase):
    """Test Suit for Admin Panel."""

    def setUp(self):
        """
        Creates a superuser & a user.
        Logs in with the superuser/admin.
        """
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='user@example.com', password='Whatever!'
        )

        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com', password='SuperUser!'
        )
        self.client.force_login(self.admin_user)

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse('admin:core_user_changelist')  # /admin/core/user/
        print('>>>>', reverse('admin:core_user_changelist'))

        res = self.client.get(url)

        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
