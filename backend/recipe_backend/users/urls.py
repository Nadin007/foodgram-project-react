from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, FollowListSet

v1_router = DefaultRouter()

v1_router.register(
    r'users/subscriptions', FollowListSet,
    basename="subscriptions"
)

v1_router.register(r'users', CustomUserViewSet, basename="users")

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
