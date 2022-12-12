"""Views for the recipe APIs"""
from django.db.models import Count

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import (Recipe, Tag, Ingredient)
from .serializers import (
    RecipeDetailSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,)


class BaseRecipeOrAttrViewSet(ModelViewSet):
    """Base view set for recipe and its attributes."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset by current user id
        (current user can see only his specified items)
        """
        return self.queryset.filter(user=self.request.user.id).order_by('-id')

    def perform_create(self, serializer):
        """Provide serializer with current user."""
        serializer.save(user=self.request.user)


class RecipeViewSet(BaseRecipeOrAttrViewSet):
    """View set for the recipe API"""
    queryset = Recipe.objects.all().prefetch_related("tags", "ingredients")

    def get_serializer_class(self):
        """Determines which serializer to use"""
        if self.action == 'list':
            return RecipeSerializer
        return RecipeDetailSerializer


class TagViewSet(BaseRecipeOrAttrViewSet):
    """View set for the tag API"""
    queryset = Tag.objects.all().annotate(recipe_count=Count('recipes'))
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeOrAttrViewSet):
    """View set for the Ingredient API"""
    queryset = Ingredient.objects.all().annotate(recipe_count=Count('recipes'))
    serializer_class = IngredientSerializer
