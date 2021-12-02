from recipe_features.models import Follow, Recipe
from recipe_features.serializers import RecipeViewSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class FollowViewSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField('get_recipe', read_only=True)
    recipes_count = serializers.SerializerMethodField(
        'recipes_amount', read_only=True)
    is_subscribed = serializers.SerializerMethodField(
        'get_subscribed', read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()

    def recipes_amount(self, data):
        return Recipe.objects.filter(author=data.id).count()

    def get_recipe(self, data):
        request = self.context.get('request')
        if not request:
            return []
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=data.id)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeViewSerializer(
            recipes, many=True).data


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('author', 'user')
    validators = [
        UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('user', 'author'),
            message="Subscription must be unique"
        )
    ]

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            raise serializers.ValidationError(
                "User should be authorised.")
        if (request.user == data['author']
           and request.method == 'GET'):
            raise serializers.ValidationError(
                'User can not subscribe to himself.')
        return data
