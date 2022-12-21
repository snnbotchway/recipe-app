"""Admin site configuration for the recipe app."""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Ingredient,
    IngredientImage,
    Recipe,
    RecipeImage,
    Tag,
)


class TagInline(admin.TabularInline):
    """Inline class for recipe tags and tag recipes."""

    model = Recipe.tags.through
    autocomplete_fields = ['tag', 'recipe']
    extra = 1


class IngredientInline(admin.TabularInline):
    """Inline class for recipe ingredients and ingredient recipes."""

    model = Recipe.ingredients.through
    autocomplete_fields = ['ingredient', 'recipe']
    extra = 1


class BaseImageInline(admin.TabularInline):
    """Base class for creating image inlines."""

    readonly_fields = ['thumbnail']
    extra = 1

    def thumbnail(self, instance):
        """Return thumbnail of instance's image."""

        if instance.image.name != '':
            return format_html(
                f"<a href='{instance.image.url}'><img src={instance.image.url} class='thumbnail'></a>")  # noqa


class RecipeImageInline(BaseImageInline):
    """Recipe image inline."""
    model = RecipeImage


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe model configuration for the admin site"""

    autocomplete_fields = ['user']
    inlines = [IngredientInline, TagInline, RecipeImageInline]
    list_display = ['title', 'user', 'id', 'price', 'time_minutes']
    list_editable = ['price', 'time_minutes']
    list_select_related = ['user']
    search_fields = ['title__icontains']

    class Media:
        css = {
            'all': ['recipe/styles.css']
        }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag model configuration for the admin site"""
    autocomplete_fields = ['user']
    inlines = [TagInline]
    list_display = ['name', 'user', 'id']
    list_select_related = ['user']
    search_fields = ['name__icontains']


class IngredientImageInline(BaseImageInline):
    """Ingredient image inline."""
    model = IngredientImage


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ingredient model configuration for the admin site"""

    autocomplete_fields = ['user']
    inlines = [IngredientImageInline, IngredientInline]
    list_display = ['name', 'user', 'id']
    list_select_related = ['user']
    search_fields = ['name__icontains']

    class Media:
        css = {
            'all': ['recipe/styles.css']
        }
