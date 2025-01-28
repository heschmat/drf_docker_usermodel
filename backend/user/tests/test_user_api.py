"""
Test suit for the user api.
"""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


# Tests that do NOT require user authentication.
class PublicUserAPITests(TestCase):
    """Tests public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_ok(self):
        """Test user can be created from payload."""
        payload = {
            'email': 'user@example.com',
            'password': 'Whatever!',
            'name': 'user-test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        # Make sure the user creation is successful.
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Make sure generated user has the same credentials as in the payload.
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        # Make sure password field is not returned.
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_err(self):
        """Make sure cannot create a new user with registered user's email."""
        payload = {
            'email': 'user@example.com',
            'password': 'Whatever!',
            'name': 'user-test'
        }
        _ = create_user(**payload)
        # Try creating a new user with already registered user's email.
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_short_password_fail(self):
        """
        Make sure user password is not too short.
        The conditions for *password* is set in `UserSerializer` in `extra_kwargs`.
        code: min_length; we set it so that password should be at least 8 char long.
        """
        payload = {
            'email': 'user@example.com',
            'name': 'user-test',
            'password': '1234567',  # a short password
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, msg=res.data)

        # Make sure that the user has not been created.
        user = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user.exists())
