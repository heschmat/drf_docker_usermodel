"""
Test suit for the user api.
"""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


URLS = {
    'create_user': reverse('user:create'),
    'token': reverse('user:token'),
    'profile': reverse('user:me'),
}


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
        res = self.client.post(URLS['create_user'], payload)

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
        res = self.client.post(URLS['create_user'], payload)

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

        res = self.client.post(URLS['create_user'], payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, msg=res.data)

        # Make sure that the user has not been created.
        user = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user.exists())

    def test_create_token_for_user(self):
        """Test generates auth token for valid credentials."""
        payload = {
            'email': 'user@example.com',
            'password': 'Whatever!',
            'name': 'user-test'
        }

        _ = create_user(**payload)
        # Authenticate with the same/correct payload.
        res = self.client.post(URLS['token'], payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_bad_credentials_fail(self):
        """Test auth fails if bad credentials sent."""
        payload = {
            'email': 'user@example.com',
            'password': 'Whatever!',
            'name': 'user-test'
        }
        _ = create_user(**payload)

        # Authenticate with an incorrect password.
        payload_bad = {'email': payload['email'], 'password': 'WrongPass!'}
        res = self.client.post(URLS['token'], payload_bad)

        # Make sure authentication fails & token is not sent back.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_get_user_unauthorized_fail(self):
        """Test authentication is required to see profile."""
        res = self.client.get(URLS['profile'])

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserAPITests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='Whatever!',
            name='Test User',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_profile_ok(self):
        """Test logged users can get/see their profile."""
        res = self.client.get(URLS['profile'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_profile_endpoint_not_allowed(self):
        """
        Test POST is not allowed for /api/user/me/ endpoint.
        Endpoint responsible for creating a new user is: /api/user/create/
        """
        res = self.client.post(URLS['profile'], {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_ok(self):
        """Test authenticated users can update their profile."""
        # Update/path new user info to the /api/user/me/
        payload_updated = {'name': 'New Name', 'password': 'AnotherPass!'}

        res = self.client.patch(URLS['profile'], payload_updated)
        # Fetch the updated data from db.
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload_updated['name'])
        self.assertTrue(self.user.check_password(payload_updated['password']))
