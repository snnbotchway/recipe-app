"""Serializers for the recipe app APIs."""

from rest_framework import serializers

from .models import (
    Ingredient,
    IngredientImage,
    Recipe,
    RecipeImage,
    Tag,
)


class BaseRecipeAttrSerializer(serializers.ModelSerializer):
    """Base serializer for recipe's many to many relations."""

    recipe_count = serializers.IntegerField(read_only=True)

    class Meta:
        fields = [
            'id',
            'name',
            'recipe_count',
        ]


class IngredientImageSerializer(serializers.ModelSerializer):
    """Serializer for ingredient images."""

    class Meta:
        model = IngredientImage
        fields = ['id', 'image']

    def create(self, validated_data):
        """
        Create and return an image for an ingredient by getting
        it's id from the view.
        """
        return IngredientImage.objects.create(
            ingredient_id=self.context['ingredient_id'], **validated_data)


class IngredientSerializer(BaseRecipeAttrSerializer):
    """Ingredient serializer"""

    images = IngredientImageSerializer(many=True, read_only=True)

    class Meta(BaseRecipeAttrSerializer.Meta):
        model = Ingredient
        fields = BaseRecipeAttrSerializer.Meta.fields + ["images"]


class TagSerializer(BaseRecipeAttrSerializer):
    """Tag serializer"""

    class Meta(BaseRecipeAttrSerializer.Meta):
        model = Tag


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for recipe images."""

    class Meta:
        model = RecipeImage
        fields = ['id', 'image']

    def create(self, validated_data):
        """
        Create and return an image for an recipe by getting
        it's id from the view.
        """
        return RecipeImage.objects.create(
            recipe_id=self.context['recipe_id'], **validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    """Simple recipe serializer(No description nor ingredients)."""

    tags = TagSerializer(many=True)
    images = RecipeImageSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',
            'images',
        ]


class RecipeDetailSerializer(RecipeSerializer):
    """Recipe detail serializer"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)
    images = RecipeImageSerializer(many=True, read_only=True)

    class Meta(RecipeSerializer.Meta):
        """Extend list of the simple serializer."""

        fields = RecipeSerializer.Meta.fields + [
            "description",
            "ingredients",
            "images",
        ]

    def _get_user(self):
        """Return current user if any."""
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def _get_or_create_tags(self, instance, tags):
        """Get or create tags."""
        user = self._get_user()

        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(**tag, user=user)
            instance.tags.add(tag_object)

    def _get_or_create_ingredients(self, instance, ingredients):
        """Get or create ingredients."""
        user = self._get_user()

        for ingredient in ingredients:
            ingredient_object, created = Ingredient.objects.get_or_create(
                **ingredient, user=user)
            instance.ingredients.add(ingredient_object)

    def create(self, validated_data):
        """Handle recipe creation and its many to many relations."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        instance = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(instance, tags)
        self._get_or_create_ingredients(instance, ingredients)
        return instance

    def update(self, instance, validated_data):
        """Handle recipe updates and those of its many to many relations."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(instance, tags)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(instance, ingredients)
        return instance
