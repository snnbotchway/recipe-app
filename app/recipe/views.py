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


class RecipeViewSet(ModelViewSet):
    """View set for the recipe API"""
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all().prefetch_related("tags")

    def get_queryset(self):
        """
        Filter recipes by current user id
        (current user can see only his recipes)
        """
        return self.queryset.filter(user=self.request.user.id).order_by('-id')

    def get_serializer_class(self):
        """Determines which serializer to use"""
        if self.action == 'list':
            return RecipeSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(ModelViewSet):
    """View set for the tag API"""
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all().annotate(recipe_count=Count('recipes'))
    serializer_class = TagSerializer

    def get_queryset(self):
        """
        Filter tags by current user id
        (current user can see only his tags)
        """
        return self.queryset.filter(user=self.request.user.id).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IngredientViewSet(ModelViewSet):
    """View set for the Ingredient API"""
    permission_classes = [IsAuthenticated]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        """
        Filter ingredients by current user id
        (current user can see only his ingredients)
        """
        return self.queryset.filter(user=self.request.user.id).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
