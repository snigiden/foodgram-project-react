from .serializers import RecipeSerializer, TagSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view

from recipes.models import Tag, Recipe
from users.models import User


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = TagSerializer
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'GET':
            return RecipeSerializer
        return RecipeSerializer