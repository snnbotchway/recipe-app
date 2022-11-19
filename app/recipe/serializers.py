"""Serializers for the recipe app APIs."""

from rest_framework import serializers

from .models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Simple recipe serializer(No description)"""
    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link'
        ]
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Recipe detail serializer"""
    class Meta(RecipeSerializer.Meta):
        RecipeSerializer.Meta.fields.append('description')
