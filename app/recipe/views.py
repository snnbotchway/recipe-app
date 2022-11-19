"""Views for the recipe APIs"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Recipe
from .serializers import RecipeDetailSerializer, RecipeSerializer


class RecipeViewSet(ModelViewSet):
    """View for the recipe APIs"""
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """
        Filter recipes by current user id
        (current user can see only his recipes)
        """
        return self.queryset.filter(user=self.request.user.id).order_by('-id')

    def get_serializer_class(self):
        """Determines which serializer to use"""
        if self.action == 'list':
            return RecipeSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
