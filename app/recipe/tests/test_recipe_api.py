"""Recipe API tests."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipe.models import (
    Recipe, Tag, Ingredient)
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


def create_tag(user, name):
    """Creates and returns new tag"""
    return Tag.objects.create(user=user, name=name)


def create_ingredient(user, name):
    """Creates and returns new tag"""
    return Ingredient.objects.create(user=user, name=name)


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
        Payloads used by numerous functions are also created.
        """
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email='test1@example.com',
            password='testPass123')
        self.user2 = get_user_model().objects.create_user(
            email='test2@example.com',
            password='testPass123')
        self.client.force_authenticate(user=self.user1)

        self.recipe_payload_with_tags = {
            "title": "Sample recipe title",
            "time_minutes": 1,
            "description": "Same recipe description",
            "price": Decimal(1),
            "link": "https://recipelink.com",
            "tags": [{"name": "Tag1"}, {"name": "Tag2"}],
        }
        self.update_tag_payload = {
            "tags": [{"name": "NewTag1"}, {"name": "NewTag2"}]}

        self.recipe_payload_with_ingredients = {
            "title": "Sample recipe title",
            "time_minutes": 1,
            "description": "Same recipe description",
            "price": Decimal(1),
            "link": "https://recipelink.com",
            "ingredients": [
                {"name": "Ingredient1"},
                {"name": "Ingredient2"}
            ],
        }
        self.update_ingredient_payload = {
            "ingredients": [
                {"name": "NewIngredient1"},
                {"name": "NewIngredient2"}
            ]}

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

    def test_create_recipe_with_non_existing_tags(self):
        """
        Test users can create recipe with new tags.
        Tags which do not exist should be created.
        """
        payload = self.recipe_payload_with_tags

        response = self.client.post(RECIPES_URL, payload, format="json")

        recipe = Recipe.objects.get(id=response.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.description, payload["description"])
        payload_tag_array = payload["tags"]
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if tags were created:
                self.assertEqual(
                    payload_tag_array[index][key], tags[index].name)
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)

    def test_create_recipe_with_existing_tags(self):
        """
        Test users can create recipe with existing tags.
        These tags should not be created again to avoid duplicates.
        """
        create_tag(name="Tag1", user=self.user1)
        create_tag(name="Tag2", user=self.user1)
        payload = self.recipe_payload_with_tags

        response = self.client.post(RECIPES_URL, payload, format="json")

        recipe = Recipe.objects.get(id=response.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(tags.count(), 2)
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.link, payload["link"])
        payload_tag_array = payload["tags"]
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)

    def test_create_recipe_with_some_existing_tags(self):
        """Tags which do not exist should be created and vice-versa"""
        create_tag(name="Tag1", user=self.user1)
        payload = self.recipe_payload_with_tags

        response = self.client.post(RECIPES_URL, payload, format="json")

        recipe = Recipe.objects.get(id=response.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(tags.count(), 2)
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(recipe.price, payload["price"])
        payload_tag_array = payload["tags"]
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)

    def test_update_recipe_without_tags(self):
        """
        Test users can add tags to recipes without tags.
        Tags which do not exist should be created.
        """
        recipe = create_recipe(user=self.user1)
        payload = self.update_tag_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(tags.count(), 2)
        payload_tag_array = payload["tags"]
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if tags were created:
                self.assertEqual(
                    payload_tag_array[index][key], tags[index].name)
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)

    def test_update_recipe_with_non_existing_tags(self):
        """
        Test users can update recipe with new tags.
        Tags which do not exist should be created.
        """
        recipe = create_recipe(user=self.user1)
        tag1 = create_tag(user=self.user1, name="OldTag1")
        tag2 = create_tag(user=self.user1, name="OldTag2")
        recipe.tags.add(tag1, tag2)
        payload = self.update_tag_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tags.count(), 4)
        payload_tag_array = payload["tags"]
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)

    def test_update_recipe_with_existing_tags(self):
        """
        Test users can update recipe with existing tags.
        These tags should not be created again to avoid duplicates.
        """
        recipe = create_recipe(user=self.user1)
        tag1 = create_tag(user=self.user1, name="OldTag1")
        tag2 = create_tag(user=self.user1, name="OldTag2")
        recipe.tags.add(tag1, tag2)
        create_tag(self.user1, "NewTag1")
        create_tag(self.user1, "NewTag2")
        payload = self.update_tag_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tags.count(), 4)
        payload_tag_array = payload["tags"]
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)

    def test_update_recipe_with_some_existing_tags(self):
        """Tags which do not exist should be created and vice-versa"""
        recipe = create_recipe(user=self.user1)
        tag1 = create_tag(user=self.user1, name="OldTag1")
        tag2 = create_tag(user=self.user1, name="OldTag2")
        recipe.tags.add(tag1, tag2)
        create_tag(self.user1, "NewTag1")
        payload = self.update_tag_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tags.count(), 4)
        payload_tag_array = payload["tags"]
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)

    def test_update_recipe_to_clear_tags(self):
        """Test if recipe is updated with no tags, its tags are cleared."""
        recipe = create_recipe(user=self.user1)
        tag1 = create_tag(user=self.user1, name="OldTag1")
        tag2 = create_tag(user=self.user1, name="OldTag2")
        recipe.tags.add(tag1, tag2)
        payload = {"tags": []}

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tags.count(), 2)
        self.assertFalse(recipe.tags.all().exists())

    def test_tags_remain_if_not_specified_in_payload(self):
        """
        Test recipe tags are not cleared when tags are not specified
        in the payload.
        """
        recipe = create_recipe(user=self.user1)
        tag1 = create_tag(user=self.user1, name="Tag1")
        tag2 = create_tag(user=self.user1, name="Tag2")
        recipe.tags.add(tag1, tag2)
        payload = {
            "title": "New recipe title",
            "description": "New description",
            "price": Decimal('2.45'),
        }

        response = self.client.patch(
            recipe_detail_url(recipe.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 2)

    def test_create_recipe_with_non_existing_ingredients(self):
        """
        Test users can create recipe with new ingredients.
        ingredients which do not exist should be created.
        """
        payload = self.recipe_payload_with_ingredients

        response = self.client.post(RECIPES_URL, payload, format="json")

        recipe = Recipe.objects.get(id=response.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.description, payload["description"])
        payload_ingredient_array = payload["ingredients"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if ingredients were created:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    ingredients[index].name)
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)

    def test_create_recipe_with_existing_ingredients(self):
        """
        Test users can create recipe with existing ingredients.
        These ingredients should not be created again to avoid duplicates.
        """
        create_ingredient(name="Ingredient1", user=self.user1)
        create_ingredient(name="Ingredient2", user=self.user1)
        payload = self.recipe_payload_with_ingredients

        response = self.client.post(RECIPES_URL, payload, format="json")

        recipe = Recipe.objects.get(id=response.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(recipe.time_minutes, payload["time_minutes"])
        self.assertEqual(recipe.link, payload["link"])
        payload_ingredient_array = payload["ingredients"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)

    def test_create_recipe_with_some_existing_ingredients(self):
        """ingredients which do not exist should be created and vice-versa"""
        create_ingredient(name="Ingredient1", user=self.user1)
        payload = self.recipe_payload_with_ingredients

        response = self.client.post(RECIPES_URL, payload, format="json")

        recipe = Recipe.objects.get(id=response.data["id"])
        serializer = RecipeDetailSerializer(recipe)
        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(recipe.price, payload["price"])
        payload_ingredient_array = payload["ingredients"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)

    def test_update_recipe_without_ingredients(self):
        """
        Test users can add ingredients to recipes without ingredients.
        ingredients which do not exist should be created.
        """
        recipe = create_recipe(user=self.user1)
        payload = self.update_ingredient_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(ingredients.count(), 2)
        payload_ingredient_array = payload["ingredients"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if ingredients were created:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    ingredients[index].name)
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)

    def test_update_recipe_with_non_existing_ingredients(self):
        """
        Test users can update recipe with new ingredients.
        ingredients which do not exist should be created.
        """
        recipe = create_recipe(user=self.user1)
        ingredient1 = create_ingredient(user=self.user1, name="OldIngredient1")
        ingredient2 = create_ingredient(user=self.user1, name="OldIngredient2")
        recipe.ingredients.add(ingredient1, ingredient2)
        payload = self.update_ingredient_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredients.count(), 4)
        payload_ingredient_array = payload["ingredients"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)

    def test_update_recipe_with_existing_ingredients(self):
        """
        Test users can update recipe with existing ingredients.
        These ingredients should not be created again to avoid duplicates.
        """
        recipe = create_recipe(user=self.user1)
        ingredient1 = create_ingredient(user=self.user1, name="OldIngredient1")
        ingredient2 = create_ingredient(user=self.user1, name="OldIngredient2")
        recipe.ingredients.add(ingredient1, ingredient2)
        create_ingredient(self.user1, "NewIngredient1")
        create_ingredient(self.user1, "NewIngredient2")
        payload = self.update_ingredient_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredients.count(), 4)
        payload_ingredient_array = payload["ingredients"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)

    def test_update_recipe_with_some_existing_ingredients(self):
        """ingredients which do not exist should be created and vice-versa"""
        recipe = create_recipe(user=self.user1)
        ingredient1 = create_ingredient(user=self.user1, name="OldIngredient1")
        ingredient2 = create_ingredient(user=self.user1, name="OldIngredient2")
        recipe.ingredients.add(ingredient1, ingredient2)
        create_ingredient(self.user1, "NewIngredient1")
        payload = self.update_ingredient_payload

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredients.count(), 4)
        payload_ingredient_array = payload["ingredients"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)

    def test_update_recipe_to_clear_ingredients(self):
        """
        Test if recipe is updated with no ingredients,
        its ingredients are cleared.
        """
        recipe = create_recipe(user=self.user1)
        ingredient1 = create_ingredient(user=self.user1, name="OldIngredient1")
        ingredient2 = create_ingredient(user=self.user1, name="OldIngredient2")
        recipe.ingredients.add(ingredient1, ingredient2)
        payload = {"ingredients": []}

        response = self.client.patch(recipe_detail_url(
            recipe_id=recipe.id), payload, format="json")

        ingredients = Ingredient.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredients.count(), 2)
        self.assertFalse(recipe.ingredients.all().exists())

    def test_ingredients_remain_if_not_specified_in_payload(self):
        """
        Test recipe ingredients are not cleared when ingredients are not
        specified in the payload.
        """
        recipe = create_recipe(user=self.user1)
        ingredient1 = create_ingredient(user=self.user1, name="ingredient1")
        ingredient2 = create_ingredient(user=self.user1, name="ingredient2")
        recipe.ingredients.add(ingredient1, ingredient2)
        payload = {
            "title": "New recipe title",
            "description": "New description",
            "price": Decimal('2.45'),
        }

        response = self.client.patch(
            recipe_detail_url(recipe.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 2)

    def test_full_recipe_update_with_tags_and_ingredients(self):
        """Test put request for full updates on recipes."""
        recipe = create_recipe(user=self.user1)
        payload = {
            "title": "Sample recipe title",
            "time_minutes": 1,
            "description": "Same recipe description",
            "price": Decimal(1),
            "link": "https://recipelink.com",
            "ingredients": [
                {"name": "Ingredient1"},
                {"name": "Ingredient2"},
            ],
            "tags": [
                {"name": "Tag1"},
                {"name": "Tag2"},
            ],
        }

        response = self.client.put(
            recipe_detail_url(recipe.id), payload, format="json")

        ingredients = Ingredient.objects.all()
        tags = Tag.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user1)
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(tags.count(), 2)
        payload_ingredient_array = payload["ingredients"]
        payload_tag_array = payload["tags"]
        for index in range(len(payload_ingredient_array)):
            for key in payload_ingredient_array[index]:
                # Test if ingredients were created:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    ingredients[index].name)
                # Test if recipe has the ingredients:
                self.assertEqual(
                    payload_ingredient_array[index][key],
                    recipe.ingredients.all()[index].name)
        for index in range(len(payload_tag_array)):
            for key in payload_tag_array[index]:
                # Test if tags were created:
                self.assertEqual(
                    payload_tag_array[index][key],
                    tags[index].name)
                # Test if recipe has the tags:
                self.assertEqual(
                    payload_tag_array[index][key],
                    recipe.tags.all()[index].name)
