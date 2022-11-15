"""Views for the user API."""

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from .serializers import UserSerializer, UserTokenSerializer


class CreateUserView(CreateAPIView):
    """Create a new user."""
    serializer_class = UserSerializer


class UserProfileView(RetrieveUpdateAPIView):
    """Manage user profile."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user


class CreateUserTokenView(ObtainAuthToken):
    """Get token for valid user email and password."""
    serializer_class = UserTokenSerializer

    # To get the browsable API;
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
