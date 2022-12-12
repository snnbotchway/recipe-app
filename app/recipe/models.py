"""Models for the recipe app"""

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.PositiveSmallIntegerField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[
            MinValueValidator(0, 'The price cannot be negative')
        ])
    description = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(
        "Tag", related_name="recipes", blank=True)

    def __str__(self):
        """Return recipe title as object name"""
        return self.title


class Tag(models.Model):
    """Tag object."""
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        """Set no user can have duplicate tags constraint"""
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'], name='unique tags'
            )
        ]

    def __str__(self):
        """Return tag name as object name"""
        return self.name


class Ingredient(models.Model):
    """Ingredient object."""
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        """Set no user can have duplicate ingredient constraint"""
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'], name='unique ingredients'
            )
        ]

    def __str__(self):
        """Return ingredient name as object name"""
        return self.name
