from .serializers import RecipeShowSerializer, RecipeCreateSerializer, TagSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Tag, Recipe
from users.models import User
from users.serializers import UserShowSerializer, UserCreateSerializer, ChangePasswordSerializer

# Вьюсет для приложения Users

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserShowSerializer
        return UserCreateSerializer
    
    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = UserShowSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'],
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        self.obj = request.user
        if serializer.is_valid():
            current_password = serializer.data.get('current_password')
            if not self.obj.check_password(current_password):
                return Response('wrong password', status=status.HTTP_401_UNAUTHORIZED)
            self.obj.set_password(serializer.data.get('new_password'))
            self.obj.save()
            return Response('password changed', status=status.HTTP_204_NO_CONTENT)
        return Response('wrong data format', status=status.HTTP_400_BAD_REQUEST)


# Вьюсет для приложения Recipes

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    




class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        #if self.action == 'GET':
        #    return RecipeShowSerializer
        return RecipeCreateSerializer
    
    #@action(detail=False, methods=['post'],
    #        )