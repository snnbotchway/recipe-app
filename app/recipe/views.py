"""Views for the recipe APIs"""
from django.db.models import Count

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import (
    Ingredient,
    IngredientImage,
    Recipe,
    RecipeImage,
    Tag,
)
from .permissions import (
    IsRecipeOwner,
    IsIngredientOwner,
)

from .serializers import (
    RecipeDetailSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeImageSerializer,
    IngredientImageSerializer,
)


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

    queryset = Recipe.objects.all().prefetch_related(
        "tags", "ingredients", "images")

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


class RecipeImageViewSet(ModelViewSet):
    """View set for recipe images."""

    serializer_class = RecipeImageSerializer
    permission_classes = [IsRecipeOwner]
    queryset = RecipeImage.objects.all()

    # get the recipe id from the url:
    def get_queryset(self):
        return self.queryset.filter(recipe_id=self.kwargs['recipe_pk'])

    # give the serializer the recipe id from the url:
    def get_serializer_context(self):
        return {'recipe_id': self.kwargs['recipe_pk']}


class IngredientImageViewSet(ModelViewSet):
    """View set for ingredient images."""

    serializer_class = IngredientImageSerializer
    permission_classes = [IsIngredientOwner]
    queryset = IngredientImage.objects.all()

    # get the ingredient id from the url:
    def get_queryset(self):
        return self.queryset.filter(ingredient_id=self.kwargs['ingredient_pk'])

    # give the serializer the ingredient id from the url:
    def get_serializer_context(self):
        return {'ingredient_id': self.kwargs['ingredient_pk']}
