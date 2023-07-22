from rest_framework import serializers
from recipes.models import Recipe, Tag, RecipeIngredient, Ingredient
from tanks.models import Favorite, Cart
from users.serializers import UserShowSerializer
from drf_extra_fields.fields import Base64ImageField



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientShowSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    name = serializers.CharField()
    measurement_unit = serializers.CharField()
    
    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )

class RecipeShowSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserShowSerializer(read_only=True)
    ingredients = RecipeIngredientShowSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated:
            self.user = self.context.get('request').user
            return Favorite.objects.filter(user=self.user, recipe=obj).exists()
        return False
    
    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated:
            self.user = self.context.get('request').user
            return Cart.objects.filter(user=self.user, recipe=obj).exists()
        return False


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

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
        ingredients = [item['id'] for item in obj.get('ingredients')]
        unique_ingredients = set(ingredients)
        if len(ingredients) != len(unique_ingredients):
            raise serializers.ValidationError(
                'ingredients must be unique'
            )
        return obj
    
    def tags_ingredients_setup(self, tags, ingredients, recipe):
        recipe.tags.set(tags)
        #RecipeIngredient.objects.bulk_create(
        #    [RecipeIngredient(
        #        recipe=recipe,
        #        amount=single_ingredient['amount'],
        #        ingredient=Ingredient.objects.get(pk=single_ingredient['id'])
        #    ) for single_ingredient in ingredients]
        #)
        #for item in ingredients:
        #    amount = item.get('amount')
        #    ingredient_id = item.get('id')
        #    #ingredient = Ingredient.objects.get(pk=ingredient_id)
        #    RecipeIngredient.objects.create(
        #        recipe=recipe,
        #        ingredient_id=ingredient_id,
        #        amount=amount,
        #    )
#
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)
        #self.tags_ingredients_setup(tags, ingredients, recipe)
        for object in ingredients:
            object_id = object.get('id')
            object_ingredient = Ingredient.objects.get(pk=object_id)
            object_amount = object.get('amount')
            object_recipe = RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=object_ingredient,
            )
            object_recipe.amount = object_amount
            object_recipe.save()


        return recipe
#    
#    def update(self, instance, validated_data):
#        instance.name = validated_data('name', instance.name)
#        instance.image = validated_data('image', instance.image)
#        instance.text = validated_data('text', instance.text)
#        instance.cooking_time = validated_data('cooking_time', instance.cooking_time)
#        tags = validated_data.pop('tags')
#        ingredients = validated_data.pop('ingredients')
#        RecipeIngredient.objects.filter(recipe=instance).delete()
#        self.tags_ingredients_setup(tags, ingredients, instance)
#        instance.save()
#        return instance
