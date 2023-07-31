from django_filters.rest_framework import FilterSet, filters
from rest_framework import filters as r_f_f

from recipes.models import Recipe, Tag
from users.models import User


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    def is_favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if value:
            return queryset.filter(cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')


class NameSearcher(r_f_f.SearchFilter):
    search_param = 'name'
