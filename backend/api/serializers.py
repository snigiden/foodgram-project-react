from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from tanks.models import Cart, Favorite
from users.models import Follow, User

"""
Блок сериализаторов для операций с пользователем.
"""


class UserShowSerializer(serializers.ModelSerializer):
    """GET сериализатор информации пользователя"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
    """Проверяем статус подписки на пользователя"""
    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and self.context['request'].user.is_authenticated):
            return Follow.objects.filter(
                follower=self.context['request'].user,
                following=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """POST сериализатор создания пользователя"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        password = validated_data['password']
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate(self, obj):
        #if not obj.get('user').check_password(obj.get('current_password')):
        #    raise serializers.ValidationError(
        #        {'current_password': 'wrong password'}
        #    )
        user = obj.user
        if not user.check_password(obj.get('current_password')):
            raise serializers.ValidationError(
                {'current_password': 'wrong password'}
            )
        if (obj['current_password']
           == obj['new_password']):
            raise serializers.ValidationError(
                {'errors': 'passwords must be different'}
            )
        return obj
    


"""
Блок сериализаторов для операций с рецептами.
"""


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientShowSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientShowSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов с привязкой к рецепту"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.CharField

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeShowSerializer(serializers.ModelSerializer):
    """Сериализатор полного отображения рецепта"""
    id = serializers.IntegerField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = UserShowSerializer()
    ingredients = RecipeIngredientShowSerializer(many=True, source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField()
    image = Base64ImageField()
    text = serializers.CharField()
    cooking_time = serializers.CharField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
    """Проверяем статус нахождения в избранном"""
    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated:
            return Favorite.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        return False
    """Проверяем статус нахождения в корзине"""
    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated:
            return Cart.objects.filter(
                user=self.context['request'].user,
                recipe=obj
            ).exists()
        return False


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для создания рецепта"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """POST сериализатор для создания рецепта"""
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        required=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    image = Base64ImageField(required=True)
    name = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, obj):
        ingredients = [
            ingredient['id'] for ingredient in obj.get('ingredients')
        ]
        unique_ingredients = set(ingredients)
        if len(ingredients) != len(unique_ingredients):
            raise serializers.ValidationError(
                {'errors': 'ingredients must be unique'}
            )
        tags = obj.get('tags')
        unique_tags = set(tags)
        if len(tags) != len(unique_tags):
            raise serializers.ValidationError(
                {'errors': 'tags must be unique'}
            )
        if obj.get('cooking_time') < 1:
            raise serializers.ValidationError(
                {'errors': 'time for cooking must have positive value'}
            )
        return obj
    """Создаём привязку тегов и ингредиентов к рецепту"""
    def tags_ingredients_setup(self, tags, ingredients, recipe):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(id=item['id']),
            amount=item['amount'])
            for item in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.tags_ingredients_setup(tags, ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()
        ).delete()
        self.tags_ingredients_setup(tags, ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeShowSerializer(
            instance,
            context=self.context
        ).data


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор вывода рецепта"""
    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор ленты подписок"""
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
    """Проверяем статус подписки"""
    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            follower=self.context['request'].user,
            following=obj.following
        ).exists()
    """Получаем список рецептов пользователя"""
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.following)
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSmallSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data
    """Считаем количество опубликованных рецептов"""
    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()
