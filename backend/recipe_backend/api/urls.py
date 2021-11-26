from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (FollowViewSet, IngredientViewSet, LoginApiView,
                    LogoutApiView, RecipeViesSet, TagsViewSet, UserViewSet)

v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet, basename="users")
v1_router.register(r'tags', TagsViewSet, basename='tags')
v1_router.register(r'ingredients', IngredientViewSet, basename="ingredients")
v1_router.register(r'recipes', RecipeViesSet, basename="recipes")
v1_router.register(r'subscriptions', FollowViewSet, basename="subscriptions")

authpatterns = [
    path(
        "refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", LoginApiView.as_view(), name="token_obtain_pair"),
    path("logout/", LogoutApiView.as_view(), name="token_black_list"),
   ]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/token/', include(authpatterns)),
]
