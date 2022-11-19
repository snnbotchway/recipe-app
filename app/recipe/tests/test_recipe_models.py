"""
Model Tests
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from recipe.models import Recipe


class ModelTests(TestCase):
    """Test models"""

    def test_create_recipe_successful(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(email='test@example.com',
                                                    password='testPass123')
        title = 'Sample recipe name'
        time_minutes = 5
        price = Decimal('23.5')
        description = 'Sample recipe description.'

        recipe = Recipe.objects.create(
            user=user,
            title=title,
            time_minutes=time_minutes,
            price=price,
            description=description)

        self.assertEqual(recipe.title, str(recipe))
        self.assertEqual(recipe.user, user)
        self.assertEqual(recipe.title, title)
        self.assertEqual(recipe.time_minutes, time_minutes)
        self.assertEqual(recipe.price, price)
        self.assertEqual(recipe.description, description)
