"""
Model Tests
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from recipe.models import Recipe, Tag


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

        recipe = Recipe.objects.create(
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
