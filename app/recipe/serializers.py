"""Serializers for the recipe app APIs."""

from rest_framework import serializers

from .models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""
    recipe_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'recipe_count'
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

    class Meta(RecipeSerializer.Meta):
        """Extend list of the simple serializer."""
        fields = RecipeSerializer.Meta.fields + ["description", "tags"]

    def get_or_create_tags(self, instance, tags):
        """Get or create tags."""
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        for tag in tags:
            tag_object, created = Tag.objects.get_or_create(**tag, user=user)
            instance.tags.add(tag_object)

    def create(self, validated_data):
        """Handle recipe creation and tag relationship if any."""
        tags = validated_data.pop('tags', [])
        instance = Recipe.objects.create(**validated_data)
        self.get_or_create_tags(instance, tags)
        return instance

    def update(self, instance, validated_data):
        """Handle recipe and tag updates."""
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.clear()
            self.get_or_create_tags(instance, tags)
        return instance
