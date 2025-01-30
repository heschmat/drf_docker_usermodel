"""
Serializers for the user API view.
"""

from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers

from django.utils.translation import gettext_lazy as _


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

    def update(self, instance, validated_data):
        """Update & return the user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        # Return the user back (it may be required for the view).
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    # Hides the pass when typed in.
    # Does not remove whitespaces as it may well be part of user password.
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Validate & authenticate the user.
        attr: a dictionary containing the user input (email & password)
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,  # we've customized user model (email instead of username)
            password=password,
        )

        # If authentication fails, user will be None.
        if not user:
            # Send 400_BAD_REQUEST & in the view show this message (translated).
            msg = _('Credentials do NOT match!')
            raise serializers.ValidationError(msg, code='authorization')

        # Add the authenticated user object to `attr`.
        # This allows the view that calls this serializer to retrieve the authenticated user.
        attrs['user'] = user
        return attrs
