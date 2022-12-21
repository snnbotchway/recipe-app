"""URL configuration for the recipe app APIs"""

from rest_framework_nested import routers


from .views import (
    IngredientViewSet,
    IngredientImageViewSet,
    RecipeViewSet,
    RecipeImageViewSet,
    TagViewSet,
)


app_name = 'recipe'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

# Nested recipe router for a recipe's images(/recipes/{id}/images/)
recipe_router = routers.NestedDefaultRouter(
    router, "recipes", lookup="recipe")
recipe_router.register("images", RecipeImageViewSet, basename="recipe-images")

# Nested ingredient router for an ingredient's images(/ingredient/{id}/images/)
ingredient_router = routers.NestedDefaultRouter(
    router, "ingredients", lookup="ingredient")
ingredient_router.register(
    "images", IngredientImageViewSet, basename="ingredient-images")

urlpatterns = router.urls + recipe_router.urls + ingredient_router.urls
