"""
Test suit for the project models.
"""

from django.test import TestCase

from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_ok(self):
        """"""
        email = 'user@example.com'
        password = "Whatever!"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = (
            'test1@EXAMPLE.com',
            'Test2@Example.Com',
            'TEST3@EXAMPLE.COM',
            'test4@example.COM',
        )

        for email in sample_emails:
            user, domain = email.split('@')
            email_normalized = user + '@' + domain.lower()
            user = get_user_model().objects.create_user(email=email, password='Whatever!')
            self.assertEqual(user.email, email_normalized)

    def test_new_user_no_email_raises_err(self):
        """Make sure email cannot be blank upon user registration."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email='', password='Whatever!')
