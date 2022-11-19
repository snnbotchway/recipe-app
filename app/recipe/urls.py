from rest_framework import routers

from .views import RecipeViewSet


app_name = 'recipe'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)

urlpatterns = router.urls
