"""Serializers for the recipe app APIs."""

from rest_framework import serializers

from .models import (
    Recipe, Tag, Ingredient)


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer"""
    recipe_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'recipe_count',
        ]


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""
    recipe_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'recipe_count',
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Simple recipe serializer(No description)"""
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',
        ]


class RecipeDetailSerializer(RecipeSerializer):
    """Recipe detail serializer"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta(RecipeSerializer.Meta):
        """Extend list of the simple serializer."""
        fields = RecipeSerializer.Meta.fields + [
            "description",
            "tags",
            "ingredients",
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
