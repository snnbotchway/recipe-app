"""Recipe API tests."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipe.models import Recipe
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer

from rest_framework import status
from rest_framework.test import APIClient


RECIPES_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """Return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Creates and returns new recipe"""
    defaults = {
        "title": "a",
        "time_minutes": 5,
        "description": "a",
        "price": Decimal('34.12'),
        "link": "https://recipe.com/recipe.pdf"
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """Test public features of the recipe API."""

    def setUp(self):
        """Setup unauthenticated client."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testPass123')

    def test_if_anonymous_user_create_recipe_returns_401(self):
        """Test anonymous user cannot create recipe."""
        payload = {
            "title": "a",
            "time_minutes": 5.5,
            "description": "a",
            "price": Decimal('34.12'),
            "link": "https://recipe.com/recipe.pdf"
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Recipe.objects.all().exists())

    def test_if_anonymous_user_get_recipes_returns_401(self):
        """Test that anonymous user cannot get recipes."""

        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(response.data["detail"])

    def test_update_recipe_if_user_is_anonymous_returns_401(self):
        """Test anonymous user cannot update given recipe"""
        recipe = create_recipe(user=self.user)
        payload = {
            "title": "e",
            "description": "e",
            "price": Decimal(2),
        }

        response = self.client.patch(
            recipe_detail_url(recipe.id), payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Recipe.objects.filter(
            title=payload["title"]).exists())
        self.assertFalse(Recipe.objects.filter(
            description=payload["description"]).exists())

    def test_delete_recipe_if_user_is_anonymous_returns_401(self):
        """Test anonymous user cannot delete given recipe"""
        recipe = create_recipe(user=self.user)

        response = self.client.delete(recipe_detail_url(recipe.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())


class PrivateRecipeAPITests(TestCase):
    """Test features of the recipe API which require authentication."""

    def setUp(self):
        """
        Authenticate client with user1 for further tests.
        User2 will be an anonymous user.
        """
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email='test1@example.com',
            password='testPass123')
        self.user2 = get_user_model().objects.create_user(
            email='test2@example.com',
            password='testPass123')
        self.client.force_authenticate(user=self.user1)

    def test_recipe_list_is_limited_to_user_and_returns_200(self):
        """Test that authenticated user can get only his/her recipes."""
        create_recipe(user=self.user1)
        create_recipe(user=self.user1)
        create_recipe(user=self.user2)
        create_recipe(user=self.user2)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user1).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_create_recipe_with_invalid_data_returns_400(self):
        """Test authenticated user cannot create recipe with invalid data"""
        payload = {
            "title": "",
            "time_minutes": 'a',
            "description": "",
            "price": Decimal(-1),
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for key in payload:
            self.assertTrue(response.data[key])

    def test_user_create_recipe_with_valid_data_returns_201(self):
        """Test authenticated user can create recipe with valid data"""
        payload = {
            "title": "a",
            "time_minutes": 1,
            "description": "a",
            "price": Decimal(1),
            "link": "a"
        }

        response = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user1)

    def test_get_recipe_detail_if_exists_returns_200(self):
        """Test get recipe detail if exists successful"""
        recipe = create_recipe(user=self.user1)

        response = self.client.get(recipe_detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail_if_not_exists_returns_404(self):
        """Test get recipe which doesn't exist returns error 404"""
        recipe = create_recipe(user=self.user1)

        response = self.client.get(recipe_detail_url(recipe.id+1))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(response.data, serializer.data)

    def test_get_other_user_recipe_detail_returns_404(self):
        """Test get recipe which doesn't belong to you returns error 404"""
        recipe = create_recipe(user=self.user2)

        response = self.client.get(recipe_detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(response.data, serializer.data)

    def test_partial_update_recipe_returns_200(self):
        """Test authenticated user can edit given recipe"""
        original_link = "https://recipe.com/recipe.pdf"
        recipe = create_recipe(user=self.user1, link=original_link)
        payload = {
            "title": "e",
            "description": "e",
            "price": Decimal('2.45'),
        }

        response = self.client.patch(
            recipe_detail_url(recipe.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.description, payload["description"])
        self.assertEqual(recipe.price, payload["price"])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user1)

    def test_full_update_recipe_returns_200(self):
        """Test authenticated user can replace given recipe"""
        recipe = create_recipe(user=self.user1)
        payload = {
            "title": "e",
            "description": "e",
            "price": Decimal('2.45'),
            "link": "new_link.recipe.com",
            "time_minutes": 54
        }

        response = self.client.put(
            recipe_detail_url(recipe.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user1)

    def test_update_recipe_user_returns_400(self):
        """Test changing the recipe user results in an error."""
        recipe = create_recipe(user=self.user1)

        payload = {'user': self.user2.id}
        self.client.patch(
            recipe_detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user1)

    def test_update_other_user_recipe_returns_404(self):
        """Test authenticated user cannot update another user's recipe"""
        recipe = create_recipe(user=self.user2)
        payload = {
            "title": "e",
            "description": "e",
            "price": Decimal(2.3),
        }

        response = self.client.patch(
            recipe_detail_url(recipe.id), payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        recipe.refresh_from_db()
        self.assertNotEqual(recipe.title, payload["title"])
        self.assertNotEqual(recipe.description, payload["description"])
        self.assertNotEqual(recipe.price, payload["price"])
        self.assertEqual(recipe.user, self.user2)

    def test_delete_recipe_returns_204(self):
        """Test authenticated user can delete a recipe"""
        recipe = create_recipe(user=self.user1)

        response = self.client.delete(recipe_detail_url(recipe.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe_returns_404(self):
        """Test authenticated user cannot delete another user's recipe"""
        recipe = create_recipe(user=self.user2)

        response = self.client.delete(recipe_detail_url(recipe.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
