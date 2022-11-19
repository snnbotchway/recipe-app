"""Admin site configuration for the recipe app."""

from django.contrib import admin

from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe model configuration for the admin site"""
    autocomplete_fields = ['user']
    search_fields = ['title__icontains']
    list_display = ['title', 'user', 'id', 'price', 'time_minutes']
    list_editable = ['price']
    list_select_related = ['user']
