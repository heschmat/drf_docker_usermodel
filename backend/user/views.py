"""
Views for the user API.
"""

from rest_framework import (
    generics,
    authentication,
    permissions,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user import serializers


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = serializers.UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = serializers.UserSerializer
    # Authentication: tell me who you are.
    authentication_classes = [authentication.TokenAuthentication]
    # Authorization: I know you; let me check if you're authorized.
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Returns the currently authenticated user."""
        return self.request.user


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = serializers.AuthTokenSerializer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES
