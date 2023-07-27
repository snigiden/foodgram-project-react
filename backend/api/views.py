from io import StringIO

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from tanks.models import Cart, Favorite
from users.models import Follow, User
from users.serializers import (ChangePasswordSerializer, UserCreateSerializer,
                               UserShowSerializer)

from .serializers import (IngredientShowSerializer, RecipeCreateSerializer,
                          RecipeShowSerializer, RecipeSmallSerializer,
                          SubscriptionSerializer, TagSerializer)

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
                return Response(
                    {'errors': 'wrong password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            self.obj.set_password(serializer.data.get('new_password'))
            self.obj.save()
            return Response(
                {'detail': 'password changed'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'wrong data format'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(follower=request.user)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, **kwargs):
        follower = request.user
        following = get_object_or_404(User, id=kwargs['pk'])
        if follower == following:
            return Response({'errors': 'cant (un)subscribe to myself'})
        subscription = Follow.objects.filter(
            follower=follower,
            following=following
        )
        if request.method == 'POST':
            if subscription:
                return Response(
                    {'errors': f'you already following {following.username}'}
                )
            sub = Follow.objects.create(follower=follower, following=following)
            serializer = SubscriptionSerializer(
                sub,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscription:
                return Response({'errors': 'already unsubscribed'})
            Follow.objects.filter(
                follower=follower,
                following=following
            ).delete()
            return Response(
                {'detail': 'successfuly unsubscribed'},
                status=status.HTTP_204_NO_CONTENT
            )

# Вьюсет для приложения Recipes


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientShowSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeShowSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeSmallSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            if not Cart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                Cart.objects.create(
                    user=request.user,
                    recipe=recipe
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'detail': 'recipe already in shopping cart'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            get_object_or_404(
                Cart,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(
                {'detail': 'recipe deleted from shopping cart'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeSmallSerializer(recipe, data=request.data)
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                Favorite.objects.create(
                    user=request.user,
                    recipe=recipe
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                'already in favorites', status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(
                Favorite,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(
                {'detail': 'recipe deleted from favorites'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=('GET',), url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        )
        buffer = StringIO()
        for item in ingredients:
            buffer.write(f"{item['ingredient__name']}\t")
            buffer.write(f"{item['amount']}\t")
            buffer.write(f"{item['ingredient__measurement_unit']}\n")
        response = FileResponse(buffer.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response
