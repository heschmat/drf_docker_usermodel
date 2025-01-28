"""
Serializers for the user API view.
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        # Add additional conditions.
        # `write_only`: the corresponding field won't be returned back in the response.
        # N.B. If validation tests fail, serializer sends 400_BAD_REQUEST.
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def create(self, validated_data):
        """Create & return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
