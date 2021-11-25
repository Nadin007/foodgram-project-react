from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from recipe_features.models import (Comment, Favorite, Follow, Ingredient,
                                    Recipe, RecipeIngredient, Tag, TagRecipe)
from users.models import User


class ConfirmationTokenSerializer(serializers.Serializer):
    """Serializing verification data to provide full user registration"""

    password = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    def validate(self, request):
        self.validate_new_password(request)
        return super().validate(request)

    def validate_new_password(self, value):
        email = value['email']
        password = value['password']
        user = generics.get_object_or_404(
                User, email=email
            )
        print(password, user.password)
        if not check_password(password, user.password):
            raise serializers.ValidationError(
                _('That is not the correct Password.')
            )
        return password


class UserSerializer(serializers.ModelSerializer):
    """Serializing data for work with user and his profile"""
    email = serializers.EmailField(
        required=True, max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        required=True, max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, max_length=150,
                                     write_only=True)
    date_joined = serializers.HiddenField(
        default=timezone.now)

    class Meta:
        model = User
        fields = (
            "email", "username", "first_name", "id",
            "last_name", "password", "avatar", "bio", "date_joined")
        read_only_fields = ("date_joined", )
        ref_name = 'ReadOnlyUsers'

    def validate(self, data):
        if data["username"] == "me":
            raise ValidationError("User can't be called 'me'")
        username = data["username"]
        password = data["password"]
        if len(username) and username.casefold() in password.casefold():
            raise serializers.ValidationError(
                _("The password is too similar to the username."))
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    current_password = serializers.CharField(
        max_length=150, write_only=True, required=True)
    new_password = serializers.CharField(
        max_length=150, write_only=True, required=True)

    def validate(self, attrs):
        self.validate_old_password(attrs)
        return super().validate(attrs)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value['current_password']):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly.'
                  'Please enter it again.')
            )


class TagsSerializes(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient."""
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""
    tags = TagsSerializes(
        many=True
    )
    ingredients = IngredientSerializer(
        many=True
    )
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            "image", "tags", "author", "name", "text", "cooking_time",
            "ingredients")
        required_fields = [
            "ingredients", "tags", "image", "name", "text", "cooking_time"]

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = generics.get_object_or_404(
                Tag, pk=tag
            )
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe
            )
        for ingredient in ingredients:

            current_ingredient = generics.get_object_or_404(
                Ingredient, pk=ingredient.id)
            RecipeIngredient.objects.create(
                ingredient=current_ingredient, amount=ingredient.amount,
                recipe=recipe
            )
        return recipe


class RecipeIngredientSerializee(serializers.ModelSerializer):
    recipe = RecipeSerializer(many=True)
    ingredient = IngredientSerializer(many=True)

    class Meta:
        model = RecipeIngredient
        fields = (
            "recipe", "ingredient", "amount"
        )


class TagRecipeSerializer(serializers.ModelSerializer):
    tag = TagsSerializes(many=True)
    recipe = RecipeSerializer(many=True)

    class Meta:
        model = TagRecipe
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field="username", read_only=True,
        default=serializers.CurrentUserDefault())
    author = SlugRelatedField(
        slug_field="username", required=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = "__all__"
    validators = [
        UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('user', 'author'),
            message="Subscription_must_be_unique"
        )
    ]

    def validate(self, data):
        if (self.context['request'].user == data['author']
           and self.context['request'].method == 'POST'):
            raise ValidationError("User can not subscribe to himself.")
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field="username", read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = SlugRelatedField(
        slug_field="id", required=True,
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = "__all__"

    def validate(self, data):
        if (
            self.context["request"].user == data["recipe"].author
           and self.context['request'].method == 'POST'):
            raise ValidationError("User can not subscribe to himself.")
        return data
