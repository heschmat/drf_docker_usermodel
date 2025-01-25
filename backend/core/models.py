"""
Database models.
"""

from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)


class UserManager(BaseUserManager):
    """Custom User Manager."""

    def create_user(self, email, password, **extra_fields):
        """Create, save & return a new user."""
        if not email:
            raise ValueError('Email cannot be blank!')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        # We pass `using=self._db` just in case  in the future we want to
        # add multiple databases. It's future proofing.
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model for our Project."""
    email = models.EmailField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # Define the field used for authentication.
    USERNAME_FIELD = 'email'
