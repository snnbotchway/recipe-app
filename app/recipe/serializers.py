"""Serializers for the recipe app APIs."""

from rest_framework import serializers

from .models import Recipe, Tag


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


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
        ]
        read_only_fields = ['id']
