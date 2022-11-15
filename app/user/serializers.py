"""Serializers for the user API view"""

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'},
        validators=[
            MinLengthValidator(
                5, 'Your password cannot be less than 5 characters'
            )
        ]
    )

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'first_name', 'last_name']
        read_only_fields = []
        """
        To make the password field write-only(is not returned to the user after
        creating or updating) and return an error if it is less than 5
        characters, add it as an extra_kwarg like below:
        """
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    """
    The following method was overridden because the default method calls
    objects.create() with the serializer fields. This will cause the
    password to be saved in clear text. However, by overriding the method,
    we ensure objects.create_user() is called instead of objects.create()
    """

    def create(self, validated_data):
        """Create an return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance: get_user_model(), validated_data):
        password = validated_data.pop("password")
        super().update(instance, validated_data)
        if password:
            instance.password = make_password(password)
            instance.save()
        return instance


class UserTokenSerializer(serializers.Serializer):
    """Serializer for authentication token"""
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
