from io import StringIO

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from tanks.models import Cart, Favorite
from users.models import Follow, User

from .filters import NameSearcher, RecipeFilter
from .pagination import LimitPaginator
from .permissions import IsOwnerOrReadOnly
from .serializers import (ChangePasswordSerializer, IngredientShowSerializer,
                          RecipeCreateSerializer, RecipeShowSerializer,
                          RecipeSmallSerializer, SubscriptionSerializer,
                          TagSerializer, UserCreateSerializer,
                          UserShowSerializer)
from .utils import create_or_delete_relation


class UserViewSet(viewsets.ModelViewSet):
    """Оперируем модель пользователей"""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = LimitPaginator

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
        serializer = ChangePasswordSerializer(
            context=request.user,
            data=request.data
        )
        if serializer.is_valid():
            serializer.update(serializer.validated_data, user=request.user)
            return Response(
                {'detail': 'password has been changed'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,),
            pagination_class=LimitPaginator)
    def subscriptions(self, request):
        queryset = Follow.objects.filter(follower=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),
            url_path='subscribe')
    def subscribe(self, request, **kwargs):
        follower = request.user
        following = get_object_or_404(User, id=kwargs['pk'])
        response = create_or_delete_relation(
            Follow, follower, following, request
        )
        response_status = response.get('status')
        if response_status == status.HTTP_200_OK:
            serializer = SubscriptionSerializer(
                response.get('instance'),
                context={"request": request}
            )
            return Response(serializer.data, status=response_status)
        return Response(response.get('string'), status=response_status)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = IngredientShowSerializer
    filter_backends = (NameSearcher,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = LimitPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeShowSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        response = create_or_delete_relation(Cart, user, recipe, request)
        response_status = response.get('status')
        if response_status == status.HTTP_200_OK:
            serializer = RecipeSmallSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(
                serializer.data,
                status=response_status
            )
        return Response(response.get('string'), status=response_status)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        response = create_or_delete_relation(Favorite, user, recipe, request)
        response_status = response.get('status')
        if response_status == status.HTTP_200_OK:
            serializer = RecipeSmallSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(
                serializer.data,
                status=response_status
            )
        return Response(response.get('string'), status=response_status)

    @action(detail=False, methods=('GET',),
            permission_classes=(permissions.IsAuthenticated,),
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        queryset = Cart.create_grocery_queryset(request.user)
        buffer = StringIO()
        for item in queryset:
            buffer.write(f"{item['ingredient__name']}\t")
            buffer.write(f"{item['amount']}\t")
            buffer.write(f"{item['ingredient__measurement_unit']}\n")
        response = FileResponse(buffer.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response
