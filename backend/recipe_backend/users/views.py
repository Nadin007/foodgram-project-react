from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (filters, generics, mixins, permissions, response,
                            status, views, viewsets)
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

from recipe_features.models import Follow
from recipe_features.pagination_hub import CustomResultsSetPagination
from users.models import User

from .permissions import AdminOrViewOrCreateOrReadOnly
from .serializerFollow import FollowSerializer, FollowViewSerializer
from .serializersUser import (ChangePasswordSerializer,
                              ConfirmationTokenSerializer, UserSerializer)


class LoginApiView(views.APIView):
    '''Provides access and refresh tokens in response to code
    confirmation and email and activate a user
    '''

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ConfirmationTokenSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = generics.get_object_or_404(User, email=email)
        refresh_token = RefreshToken.for_user(user)
        return response.Response(
            {
                'auth_token': str(refresh_token.access_token),
                'refresh_token': str(refresh_token),
            }, status=status.HTTP_201_CREATED
        )


class LogoutApiView(views.APIView):
    '''Provides access and refresh tokens in response to code
    confirmation and email and activate a user
    '''

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            token = request.auth
            token.blacklist()
            return response.Response({}, status=status.HTTP_201_CREATED)

        except Exception as e:
            raise Exception(
                f'Bad request {e}',
            )


class UserViewSet(viewsets.ModelViewSet):
    """Provides work with user and his profile depending
    on permission and role
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminOrViewOrCreateOrReadOnly]
    lookup_field = "id"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    pagination_class = CustomResultsSetPagination

    def create(self, request):
        """Create a new user and send an account activation email"""
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        users = User.objects.filter(Q(email=email) | Q(username=username))
        if not users.exists():
            serializer.save(password=make_password(password))
        else:
            user = users.first()
            if user.email != email or user.username != username:
                return response.Response(
                    serializer.data, status=status.HTTP_400_BAD_REQUEST
                )
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["GET"],
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def get_self_user_page(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["POST"],
        url_path="set_password",
        permission_classes=[permissions.IsAuthenticated],
    )
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        if hasattr(user, 'auth_token'):
            user.auth_token.blacklist()
        return response.Response(
            '', status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        url_path="subscribe",
        permission_classes=[permissions.IsAuthenticated],
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
        return User.objects.filter(follower__user=self.request.user)
