from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (filters, mixins, permissions, response, status,
                            viewsets)
from rest_framework.decorators import action

from .serializers_follow import FollowSerializer, FollowViewSerializer
from recipe_features.models import Follow
from recipe_features.pagination_hub import CustomResultsSetPagination
from recipe_features.permissions import CurrentUserOrAdminOrReadOnly
from users.models import User


class CustomUserViewSet(UserViewSet):
    """Provides work with user and his profile depending
    on permission and role
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    pagination_class = CustomResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        url_path="subscribe",
        permission_classes=[CurrentUserOrAdminOrReadOnly],
        pagination_class=None
    )
    def subscribe(self, request, id):
        if request.method == 'DELETE':
            return self.unsubscribe(request, id)
        user = self.request.user.id
        author = get_object_or_404(User, id=id)
        data = {'user': user, 'author': id}
        serializer = FollowSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, author=author)
        return response.Response(FollowViewSerializer(
            author, context={'request': request}).data,
            status=status.HTTP_201_CREATED)

    def unsubscribe(self, request, pk):
        subscribtion = get_object_or_404(
            Follow, user=request.user, author=pk)
        subscribtion.delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT)


class FollowListSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pagination_class = CustomResultsSetPagination
    serializer_class = FollowViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
