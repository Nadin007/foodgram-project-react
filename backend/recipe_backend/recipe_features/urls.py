from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViesSet, TagsViewSet

v1_router = DefaultRouter()


v1_router.register(r'tags', TagsViewSet, basename='tags')
v1_router.register(r'ingredients', IngredientViewSet, basename="ingredients")
v1_router.register(r'recipes', RecipeViesSet, basename="recipes")


urlpatterns = [
    path('', include(v1_router.urls)),
]
