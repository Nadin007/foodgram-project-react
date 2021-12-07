from django.db.models.aggregates import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, response, status, viewsets
from rest_framework.decorators import action

from .pagination_hub import CustomResultsSetPagination
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientSerializer, PostRecipeSerializer,
                          RecipeSerializer, RecipeViewSerializer,
                          TagsSerializes)
from recipe_features.download_feature.pdf_downloader import PDFDownload
from recipe_features.download_feature.utils import format_ingredient
from recipe_features.filters import IngredientSearchFilter, RecipeFilter
from recipe_features.models import (Cart, Favorite, Ingredient, Recipe,
                                    RecipeIngredient, Tag)
from recipe_features.permissions import IsAdminOrReadOnly, OwnerAdminOrReadOnly


class TagsViewSet(viewsets.ModelViewSet):
    '''Viewset for Tag.'''
    queryset = Tag.objects.all()
    serializer_class = TagsSerializes
    lookup_field = 'id'
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    '''Viewset for Ingredient.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    ordering_fields = ('name',)
    lookup_field = 'name'
    lookup_field = 'id'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name',)
    pagination_class = None


class RecipeViesSet(viewsets.ModelViewSet):
    '''Viewset for Recipe.'''
    queryset = Recipe.objects.all()
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter,
        filters.OrderingFilter)
    ordering_fields = ('-id',)
    filterset_class = RecipeFilter
    pagination_class = CustomResultsSetPagination

    permission_classes = (OwnerAdminOrReadOnly,)

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_create(serializer)
        return response.Response(RecipeSerializer(
            recipe, context={'request': request}).data,
            status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    def update(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Recipe, id=pk)
        serializer = PostRecipeSerializer(
            instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_update(serializer)
        return response.Response(RecipeSerializer(
            recipe, context={'request': request}).data,
            status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return PostRecipeSerializer

    @action(
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        methods=['GET', 'DELETE'],
        url_path="favorite",)
    def favorite(self, request, pk):
        if request.method == 'DELETE':
            return self.del_favorite(request, pk)
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id, 'recipe': recipe.id
        }
        serializer = FavoriteSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED)

    def del_favorite(self, request, pk):
        subscribtion = get_object_or_404(
            Favorite, user=request.user, recipe=pk)
        subscribtion.delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_in_cart(self, request, pk):
        if request.method == 'DELETE':
            return self.del_from_cart(request, pk)
        user = self.request.user
        purchase = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user.id, 'purchase': purchase.id
        }
        serializer = CartSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(RecipeViewSerializer(
            purchase).data,
            status=status.HTTP_201_CREATED)

    def del_from_cart(self, request, pk):
        purchase = get_object_or_404(
            Cart, user=request.user, purchase=pk)
        purchase.delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated],
    )
    def show_cart(self, request):
        list_of_ingredients = RecipeIngredient.objects.filter(
            recipe__purchases__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(
                amount=Sum('amount'))
        list_of_recipes = [format_ingredient(s) for s in list_of_ingredients]
        result = PDFDownload()
        return result.download(list_of_recipes, 'СПИСОК ПРОДУКТОВ:')
