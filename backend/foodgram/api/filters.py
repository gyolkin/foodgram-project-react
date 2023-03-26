from django_filters import CharFilter, ChoiceFilter, FilterSet, NumberFilter

from content.models import Favourite, Recipe, ShoppingList


class RecipeFilter(FilterSet):
    choices = ((0, 'False'), (1, 'True'))
    is_favorited = ChoiceFilter(choices=choices, method='filter_is_favorited')
    is_in_shopping_cart = ChoiceFilter(
        choices=choices, method='filter_is_in_shopping_cart'
    )
    author = NumberFilter(field_name='author__id')
    tags = CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            recipe_ids = Favourite.objects.filter(user=user).values_list(
                'recipe_id', flat=True
            )
            if value == '1':
                return queryset.filter(id__in=recipe_ids)
            else:
                return queryset.exclude(id__in=recipe_ids)
        return queryset.none() if value == '1' else queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            shopping_list = ShoppingList.objects.filter(user=user).first()
            if shopping_list:
                recipe_ids = shopping_list.recipes.all().values_list(
                    'id', flat=True
                )
                if value == '1':
                    return queryset.filter(id__in=recipe_ids)
                else:
                    return queryset.exclude(id__in=recipe_ids)
            return queryset.none() if value == '1' else queryset
        return queryset.none() if value == '1' else queryset
