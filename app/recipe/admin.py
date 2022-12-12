"""Admin site configuration for the recipe app."""

from django.contrib import admin

from .models import Recipe, Tag


class TagInline(admin.TabularInline):
    """Inline class for recipe tags and tag recipes."""
    model = Recipe.tags.through
    autocomplete_fields = ['tag', 'recipe']
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe model configuration for the admin site"""
    autocomplete_fields = ['user']
    inlines = [TagInline]
    list_display = ['title', 'user', 'id', 'price', 'time_minutes']
    list_editable = ['price', 'time_minutes']
    list_select_related = ['user']
    search_fields = ['title__icontains']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag model configuration for the admin site"""
    autocomplete_fields = ['user']
    inlines = [TagInline]
    list_display = ['name', 'user', 'id']
    list_select_related = ['user']
    search_fields = ['name__icontains']
