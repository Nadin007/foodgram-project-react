from django.db.models import Q
from django_filters import BooleanFilter, CharFilter
from django_filters import rest_framework as filters

from recipe_features.models import Recipe


class RecipeFilter(filters.FilterSet):
    '''
    Filter for filtring by is_favorited, author, tags and is_in_shopping_cart
    '''

    is_in_shopping_cart = BooleanFilter(method='get_in_cart')
    is_favorited = BooleanFilter(method='get_is_favourite')
    tags = CharFilter(field_name='tags__slug')

    def get_in_cart(self, queryset, field_name, value):
        if value:
            return queryset.filter(purchases__user=self.request.user)
        return queryset.filter(~Q(purchases__user=self.request.user))

    def get_is_favourite(self, queryset, field_name, value):
        if value:
            return queryset.filter(favorite_rec__user=self.request.user)
        return queryset.filter(~Q(favorite_rec__user=self.request.user))

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')
