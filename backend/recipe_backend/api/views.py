from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, generics, mixins, pagination, permissions,
                            response, status, views, viewsets)
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

from recipe_features.models import Follow, Ingredient, Recipe, Tag
from users.models import User

from .permissions import (AdminOrViewOrCreateOrReadOnly, IsAdminOrReadOnly,
                          OwnerOrReadOnly)
from .serializers import (ChangePasswordSerializer,
                          ConfirmationTokenSerializer, FollowSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagsSerializes, UserSerializer)


class LoginApiView(views.APIView):
    """Provides access and refresh tokens in response to code
    confirmation and email and activate a user
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ConfirmationTokenSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        user = generics.get_object_or_404(User, email=email)
        refresh_token = RefreshToken.for_user(user)
        return response.Response(
            {
                "auth_token": str(refresh_token.access_token),
                "refresh_token": str(refresh_token),
            }, status=status.HTTP_201_CREATED
        )


class LogoutApiView(views.APIView):
    """Provides access and refresh tokens in response to code
    confirmation and email and activate a user
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.auth
            print('ttrtrtrtrtrtr')
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return response.Response({}, status=status.HTTP_201_CREATED)

        except Exception as e:
            raise Exception(
                f"Bad request {e}",
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
    pagination_class = pagination.LimitOffsetPagination

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
        print(user)
        if hasattr(user, 'auth_token'):
            print('dsjjjsdjsadjjd')
            user.auth_token.blacklist()
        return response.Response(
            '', status=status.HTTP_204_NO_CONTENT)


class CustomizedListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Base ViewSet for Tag & Ingredient.
    Allowed actions: `list`, `create`, `delete`.
    Other actions returns HTTP 405.
    """

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ("name",)
    search_fields = ("name",)
    lookup_field = "slug"
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]


class TagsView(CustomizedListCreateDestroyViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializes


class IngredientView(CustomizedListCreateDestroyViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViesSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (OwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ListRetriveCreateViewSet(
        mixins.ListModelMixin, mixins.RetrieveModelMixin,
        mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class FollowViewSet(ListRetriveCreateViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter,
        filters.OrderingFilter)
    search_fields = ('author__username',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

