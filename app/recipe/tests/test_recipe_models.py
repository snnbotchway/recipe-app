"""
Model Tests
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from recipe.models import (
    Recipe,
    RecipeImage,
    Tag,
    Ingredient,
    IngredientImage,
)
from recipe import models

from unittest.mock import patch


def create_recipe(user, **params):
    """Creates and returns new recipe"""

    defaults = {
        "title": "Sample Recipe Name",
        "time_minutes": 20,
        "description": "Boil for 5 minutes, allow to cool for 15 minutes.",
        "price": Decimal('34.12'),
        "link": "https://recipe.com/recipe.pdf"
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class ModelTests(TestCase):
    """Test models"""

    def setUp(self):
        self.user = get_user_model().objects.create(
            email='user@example.com',
            password='testPass123',
        )

    def test_create_recipe_successful(self):
        """Test creating a recipe is successful."""
        title = 'Sample recipe name'
        time_minutes = 5
        price = Decimal('23.5')
        description = 'Sample recipe description.'

        recipe = create_recipe(
            user=self.user,
            title=title,
            time_minutes=time_minutes,
            price=price,
            description=description)

        self.assertEqual(recipe.title, str(recipe))
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.title, title)
        self.assertEqual(recipe.time_minutes, time_minutes)
        self.assertEqual(recipe.price, price)
        self.assertEqual(recipe.description, description)

    def test_create_tag_successful(self):
        """Test creating a tag is successful."""
        name = 'Sample tag name'

        tag = Tag.objects.create(
            user=self.user,
            name=name)

        self.assertEqual(tag.name, str(tag))
        self.assertEqual(tag.user, self.user)
        self.assertEqual(tag.name, name)

    def test_create_ingredient_successful(self):
        """Test creating an ingredient is successful."""
        name = 'Sample ingredient name'

        ingredient = Ingredient.objects.create(
            user=self.user,
            name=name)

        self.assertEqual(ingredient.name, str(ingredient))
        self.assertEqual(ingredient.user, self.user)
        self.assertEqual(ingredient.name, name)

    @patch("recipe.models.uuid.uuid4")
    def test_recipe_image_file_name_uuid(self, mock_uuid):
        """Test generating recipe image path."""

        recipe = create_recipe(user=self.user)

        recipe_image = RecipeImage.objects.create(recipe=recipe)
        uuid = 'test_uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(recipe_image, "example.jpg")

        self.assertEqual(
            file_path, f"uploads/recipes/{recipe.id}/{uuid}.jpg")

    @patch("recipe.models.uuid.uuid4")
    def test_ingredient_image_file_name_uuid(self, mock_uuid):
        """Test generating ingredient image path."""

        ingredient = Ingredient.objects.create(
            user=self.user, name="Sample Ingredient")

        ingredient_image = IngredientImage.objects.create(
            ingredient=ingredient)
        uuid = 'test_uuid'
        mock_uuid.return_value = uuid
        file_path = models.ingredient_image_file_path(
            ingredient_image, "example.jpg")

        self.assertEqual(
            file_path, f"uploads/recipes/{ingredient.id}/{uuid}.jpg")
