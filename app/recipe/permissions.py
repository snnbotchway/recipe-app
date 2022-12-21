from rest_framework.permissions import BasePermission

from .models import (
    Recipe,
    Ingredient,
)


class IsRecipeOwner(BasePermission):
    """
    This permission ensures only owners of recipes can access and
    alter their images.
    """

    def has_permission(self, request, view):
        """
        Returns true if current user created the recipe whose images he/she
        is trying to access.
        """
        # Get recipe_id from the view
        recipe_id = view.kwargs['recipe_pk']
        # Check if current user created the recipe with that id
        return Recipe.objects.filter(
            id=recipe_id, user=request.user.id).exists()


class IsIngredientOwner(BasePermission):
    """
    This permission ensures only owners of ingredients can access and
    alter their images.
    """

    def has_permission(self, request, view):
        """
        Returns true if current user created the ingredient whose images he/she
        is trying to access.
        """
        # Get ingredient_id from the view
        ingredient_id = view.kwargs['ingredient_pk']
        # Check if current user created the ingredient with that id
        return Ingredient.objects.filter(
            id=ingredient_id, user=request.user.id).exists()
