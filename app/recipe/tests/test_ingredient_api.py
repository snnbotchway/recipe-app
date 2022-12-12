"""ingredient API tests."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipe.models import Ingredient
from recipe.serializers import IngredientSerializer

from rest_framework import status
from rest_framework.test import APIClient


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def ingredient_detail_url(ingredient_id):
    """Return an ingredient detail URL."""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_ingredient(user, **params):
    """Creates and returns new ingredient"""
    defaults = {
        "name": "Sample ingredient",
    }
    defaults.update(params)
    return Ingredient.objects.create(user=user, **defaults)


class PublicIngredientAPITests(TestCase):
    """Test public features of the ingredient API."""

    def setUp(self):
        """Setup unauthenticated client."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testPass123")

    def test_if_anonymous_user_create_ingredient_returns_401(self):
        """Test anonymous user cannot create ingredient."""
        payload = {"name": "Sample ingredient"}

        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Ingredient.objects.all().exists())

    def test_if_anonymous_user_get_ingredients_returns_401(self):
        """Test that anonymous user cannot get ingredients."""

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(response.data["detail"])

    def test_update_ingredient_if_user_is_anonymous_returns_401(self):
        """Test anonymous user cannot update given ingredient"""
        ingredient = create_ingredient(user=self.user)
        payload = {"name": "New ingredient name"}

        response = self.client.patch(
            ingredient_detail_url(ingredient.id), payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Ingredient.objects.filter(
            name=payload["name"]).exists())

    def test_delete_ingredient_if_user_is_anonymous_returns_401(self):
        """Test anonymous user cannot delete given ingredient"""
        ingredient = create_ingredient(user=self.user)

        response = self.client.delete(ingredient_detail_url(ingredient.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Ingredient.objects.filter(id=ingredient.id).exists())


class PrivateIngredientAPITests(TestCase):
    """Test features of the ingredient API which require authentication."""

    def setUp(self):
        """
        Authenticate client with user1 for further tests.
        User2 will be an anonymous user.
        """
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email="test1@example.com",
            password="testPass123")
        self.user2 = get_user_model().objects.create_user(
            email="test2@example.com",
            password="testPass123")
        self.client.force_authenticate(user=self.user1)

    def test_ingredient_list_is_limited_to_user_and_returns_200(self):
        """Test that authenticated user can get only his/her ingredients."""
        create_ingredient(user=self.user1)
        create_ingredient(user=self.user2)

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.filter(
            user=self.user1).order_by("-id")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for index in range(len(response.data)):
            self.assertDictContainsSubset(
                serializer.data[index], response.data[index])

    def test_user_create_ingredient_with_invalid_data_returns_400(self):
        """Test authenticated user can"t create ingredient with invalid data"""
        payload = {"name": ""}

        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data["name"])

    def test_user_create_ingredient_with_valid_data_returns_201(self):
        """Test authenticated user can create ingredient with valid data"""
        payload = {"name": "ingredient name"}

        response = self.client.post(INGREDIENTS_URL, payload)

        ingredient = Ingredient.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.user, self.user1)

    def test_get_ingredient_detail_if_exists_returns_200(self):
        """Test get ingredient detail if exists successful"""
        ingredient = create_ingredient(user=self.user1)

        response = self.client.get(ingredient_detail_url(ingredient.id))

        serializer = IngredientSerializer(ingredient)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset(serializer.data, response.data)

    def test_get_ingredient_detail_if_not_exists_returns_404(self):
        """Test get ingredient which doesn't exist returns error 404"""
        ingredient = create_ingredient(user=self.user1)

        response = self.client.get(ingredient_detail_url(ingredient.id+1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        self.assertFalse(response.data.get("id"))

    def test_get_other_user_ingredient_detail_returns_404(self):
        """Test get ingredient which doesn't belong to you returns error 404"""
        ingredient = create_ingredient(user=self.user2)

        response = self.client.get(ingredient_detail_url(ingredient.id))

        self.assertTrue(response.data["detail"])
        self.assertFalse(response.data.get("id"))

    def test_partial_update_ingredient_returns_200(self):
        """Test authenticated user can edit given ingredient"""
        original_name = "Original Name"
        ingredient = create_ingredient(user=self.user1, name=original_name)
        payload = {"name": "New name"}

        response = self.client.patch(
            ingredient_detail_url(ingredient.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.user, self.user1)

    def test_full_update_ingredient_returns_200(self):
        """Test authenticated user can replace given ingredient"""
        ingredient = create_ingredient(user=self.user1)
        payload = {"name": "New name"}

        response = self.client.put(
            ingredient_detail_url(ingredient.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.user, self.user1)

    def test_cannot_update_ingredient_user(self):
        """Test changing the ingredient"s user is not possible."""
        ingredient = create_ingredient(user=self.user1)

        payload = {"user": self.user2.id}
        self.client.patch(
            ingredient_detail_url(ingredient.id), payload)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.user, self.user1)

    def test_update_other_user_ingredient_returns_404(self):
        """Test authenticated user cannot update another user"s ingredient"""
        ingredient = create_ingredient(user=self.user2)
        payload = {"name": "New name"}

        response = self.client.patch(
            ingredient_detail_url(ingredient.id), payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        ingredient.refresh_from_db()
        self.assertNotEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.user, self.user2)

    def test_delete_ingredient_returns_204(self):
        """Test authenticated user can delete an ingredient"""
        ingredient = create_ingredient(user=self.user1)

        response = self.client.delete(ingredient_detail_url(ingredient.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_delete_other_user_ingredient_returns_404(self):
        """Test authenticated user cannot delete another user"s ingredient"""
        ingredient = create_ingredient(user=self.user2)

        response = self.client.delete(ingredient_detail_url(ingredient.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        self.assertTrue(Ingredient.objects.filter(id=ingredient.id).exists())
