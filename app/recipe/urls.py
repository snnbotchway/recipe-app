"""URL configuration for the recipe app APIs"""

from rest_framework import routers

from .views import RecipeViewSet, TagViewSet


app_name = 'recipe'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = router.urls
