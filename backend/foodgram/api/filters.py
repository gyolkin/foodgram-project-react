from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet, NumberFilter)

from content.models import Favourite, Ingredient, Recipe, ShoppingList


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    author = NumberFilter(field_name='author__id')
    tags = CharFilter(field_name='tags__slug', lookup_expr='in')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            recipe_ids = Favourite.objects.filter(user=user).values_list(
                'recipe_id', flat=True
            )
            if value:
                return queryset.filter(id__in=recipe_ids)
            return queryset.exclude(id__in=recipe_ids)
        return queryset.none() if value else queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            recipe_ids = ShoppingList.objects.filter(user=user).values_list(
                'recipe_id', flat=True
            )
            if value:
                return queryset.filter(id__in=recipe_ids)
            return queryset.exclude(id__in=recipe_ids)
        return queryset.none() if value else queryset


class IngredientFilter(FilterSet):
    """Фильтр для ингредиентов."""
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
