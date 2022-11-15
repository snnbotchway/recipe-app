"""Tests for the user API"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
USER_TOKEN_URL = reverse('user:token')
USER_PROFILE_URL = reverse('user:me')


def create_user(**kwargs):
    """Creates and returns new user"""
    return get_user_model().objects.create_user(**kwargs)


class PublicUserAPITests(TestCase):
    """Test public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_returns_201(self):
        """Test creating a user is successful"""
        payload = {
            "email": "user@example.com",
            "password": "testPass123",
            "first_name": "user_first_name",
            "last_name": "user_last_name",
        }

        response = self.client.post(CREATE_USER_URL, payload)

        created_user = get_user_model().objects.get(email=payload["email"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created_user.email, payload["email"])
        self.assertTrue(created_user.check_password(payload["password"]))
        # Make sure the password is not returned to the user:
        self.assertNotIn('password', response.data)

    def test_create_user_if_email_exists_returns_400(self):
        """Test create user with an email that already exists returns error"""
        payload = {
            "email": "user@example.com",
            "password": "testPass123",
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data["email"])

    def test_create_user_with_short_password_returns_400(self):
        """Test create user with password less than 5 characters fails"""
        payload = {
            "email": "user@example.com",
            "password": "test",
        }

        response = self.client.post(CREATE_USER_URL, payload)
        user_exist = get_user_model().objects.filter(
            email=payload["email"]).exists()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exist)
        self.assertTrue(response.data["password"])

    def test_generate_token_with_valid_credentials_returns_200(self):
        """Test a token is returned with valid credentials"""
        payload = {
            "email": "user@example.com",
            "password": "passTest123",
        }
        create_user(**payload)

        response = self.client.post(USER_TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_generate_token_with_invalid_credentials_returns_400(self):
        """Test a token is not returned with invalid credentials"""
        create_user(email="user@example.com", password="goodPass123")
        payload = {
            "email": "user@example.com",
            "password": "badPass123",
        }

        response = self.client.post(USER_TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_generate_token_without_password_returns_400(self):
        """Test a token is not returned with blank password"""
        create_user(email="user@example.com", password="goodPass123")
        payload = {
            "email": "user@example.com",
            "password": "",
        }

        response = self.client.post(USER_TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_if_get_user_profile_when_anonymous_returns_401(self):
        """Test anonymous user cannot get user profile info."""
        payload = {
            "email": "user@example.com",
            "password": "testPass123",
        }
        create_user(**payload)

        response = self.client.get(USER_PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('email', response.data)
        self.assertTrue(response.data["detail"])

    def test_if_update_user_profile_when_anonymous_returns_401(self):
        """Test anonymous user cannot update user profile info."""
        old_payload = {
            "email": "oldemail@example.com",
            "password": "oldPass123",
            "first_name": "old_first_name",
            "last_name": "old_last_name",
        }
        create_user(**old_payload)
        new_payload = {
            "email": "newemail@example.com",
            "password": "newPass123",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }

        response = self.client.put(USER_PROFILE_URL, new_payload)

        user = get_user_model().objects.get(email="oldemail@example.com")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(user.email, old_payload["email"])
        self.assertEqual(user.first_name, old_payload["first_name"])
        self.assertEqual(user.last_name, old_payload["last_name"])
        self.assertTrue(user.check_password(old_payload["password"]))
        self.assertFalse(get_user_model().objects.filter(
            email=new_payload["email"]).exists())
        self.assertTrue(response.data["detail"])


class PrivateUserAPITests(TestCase):
    """Test features of the user API which require authentication"""

    def setUp(self):
        payload = {
            "email": "test@example.com",
            "password": "testPass123",
            "first_name": "user_first_name",
            "last_name": "user_last_name",
        }
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_if_get_user_profile_returns_200(self):
        """Test authenticated user can get user profile info."""
        response = self.client.get(USER_PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        # Make sure the password is not returned to the user:
        self.assertNotIn('password', response.data)

    def test_if_update_profile_returns_200(self):
        """Test authenticated user can update user profile info."""
        payload = {
            "email": "newemail@example.com",
            "password": "newPass123",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }

        response = self.client.put(USER_PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload["email"])
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_if_partial_update_returns_200(self):
        """Test authenticated user can update partial user profile info."""
        payload = {
            "password": "updatedPass123",
            "first_name": "updated_first_name",
        }

        response = self.client.patch(USER_PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_if_post_me_returns_405(self):
        """Test authenticated user can update partial user profile info."""

        response = self.client.post(USER_PROFILE_URL, {})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
