from django.urls import path
from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import FollowListSet, LoginApiView, LogoutApiView, UserViewSet

v1_router = DefaultRouter()

v1_router.register(
    r'users/subscriptions', FollowListSet,
    basename="subscriptions"
)
v1_router.register(r'users', UserViewSet, basename="users")

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
