
"""
URL mappings for the user API
"""
from .views import CreateUserView, CreateUserTokenView, UserProfileView

from django.urls import path

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateUserTokenView.as_view(), name='token'),
    path('me/', UserProfileView.as_view(), name='me'),
]
