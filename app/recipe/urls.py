"""URL configuration for the recipe app APIs"""

from rest_framework import routers

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet)


app_name = 'recipe'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = router.urls
