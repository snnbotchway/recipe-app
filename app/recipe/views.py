"""Views for the recipe APIs"""

from django.db.models import Count

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

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


# Extend API documentation with filter documentation.
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="assigned_only",
                type=OpenApiTypes.INT,
                enum=[0, 1],
                description="Filter items by those assigned to a recipe.",
                required=False,
            ),
        ],
    ),
)
class BaseRecipeOrAttrViewSet(ModelViewSet):
    """Base view set for recipe and its attributes."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return appropriate queryset considering current user and filters.
        """
        queryset = self.queryset.filter(
            user=self.request.user.id).order_by("-id")
        assigned_only = int(self.request.query_params.get("assigned_only", 0))
        if assigned_only:
            # Filter items by those that are assigned to at least
            # one recipe
            queryset = queryset.filter(recipes__isnull=False)
        return queryset

    def perform_create(self, serializer):
        """Provide serializer with current user."""
        serializer.save(user=self.request.user)


# Extend API documentation with filter documentation.
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="tags",
                type=OpenApiTypes.STR,
                description="Comma-separated list of tag IDs",
                required=False,
            ),
            OpenApiParameter(
                name="ingredients",
                type=OpenApiTypes.STR,
                description="Comma-separated list of ingredient IDs",
                required=False,
            ),
        ],
    ),
)
class RecipeViewSet(ModelViewSet):
    """View set for the recipe API"""

    permission_classes = [IsAuthenticated]

    queryset = Recipe.objects.all().prefetch_related(
        "tags", "ingredients", "images")

    def get_queryset(self):
        """Returns appropriate recipe queryset."""

        queryset = self.queryset.filter(
            user=self.request.user.id).order_by('-id')
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        if tags:
            tag_ids = tags.split(",")
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = ingredients.split(",")
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.distinct()

    def perform_create(self, serializer):
        """Provide serializer with current user."""
        serializer.save(user=self.request.user)

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
