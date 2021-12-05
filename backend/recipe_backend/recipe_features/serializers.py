from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from recipe_features.models import (Cart, Favorite, Ingredient, Recipe,
                                    RecipeIngredient, Tag)
from users.serializers_user import CustomUserSerializer


class TagsSerializes(serializers.ModelSerializer):
    '''Serializer for tags.'''
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for ingredient.'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''Serializer for bounding recipe and ingredients.'''
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'amount', 'name', 'measurement_unit'
        )


class PostRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    '''Serializer for recipes'''
    tags = TagsSerializes(
        many=True
    )
    ingredients = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField('favorite')
    is_in_shopping_cart = serializers.SerializerMethodField('shopping_list')

    def favorite(self, instance):
        if not instance or self.context["request"].user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=self.context["request"].user.id, recipe=instance.id).exists()

    def shopping_list(self, instance):
        if not instance or self.context["request"].user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=self.context["request"].user.id,
            purchase=instance.id).exists()

    def get_ingredients(self, instance):
        ingredients = RecipeIngredient.objects.filter(recipe=instance)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author', 'name', 'text', 'cooking_time',
            'ingredients', 'is_favorited', 'is_in_shopping_cart')
        required_fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time']


class PostRecipeSerializer(serializers.ModelSerializer):
    '''Serializer for creating or updating recipes'''
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = PostRecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=False, use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'name', 'text', 'cooking_time',
            'ingredients')
        required_fields = [
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time']

    def add_ingredients(self, list_of_obj, recipe):
        for ingredient in list_of_obj:
            RecipeIngredient.objects.create(
                ingredient=ingredient["id"], amount=ingredient['amount'],
                recipe=recipe
            )

    def validate(self, attrs):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        cooking_time = self.initial_data.get('cooking_time')
        if not cooking_time or cooking_time <= 0:
            raise serializers.ValidationError(
                {'Cooking_timeError':
                 'Required field and must be more than 0.'})
        if not tags:
            raise serializers.ValidationError(
                {'TagsError': 'Required field.'})
        if not ingredients:
            raise serializers.ValidationError(
                {'IngredientsError': 'Required field.'})
        while 0 < len(tags):
            tag = tags.pop()
            if tag in tags:
                raise serializers.ValidationError(
                    {'TagsError': 'The field \'tag\' must be unique.'})
        if not ingredients:
            raise serializers.ValidationError(
                {'IngredientsError': 'Required field.'})
        while 0 < len(ingredients):
            ingredient = ingredients.pop()
            if ingredient in ingredients:
                raise serializers.ValidationError(
                    {
                        'IngredientsError':
                        'The field \'ingredient\' must be unique.'})
        return super().validate(attrs)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):

        val_tags = validated_data.pop('tags')
        val_ingredients = validated_data.pop('ingredients')
        if instance.tags != val_tags:
            instance.tags.set(val_tags)
        if instance.ingredients != val_ingredients:
            RecipeIngredient.objects.filter(recipe=instance).all().delete()
            self.add_ingredients(val_ingredients, instance)
        return super().update(instance, validated_data)


'''
class TagRecipeSerializer(serializers.ModelSerializer):
    tag = TagsSerializes(many=True)
    recipe = RecipeSerializer(many=True)

    class Meta:
        model = TagRecipe
        fields = "__all__"
'''


class RecipeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field="username", read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = SlugRelatedField(
        slug_field="id", required=True,
        queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = '__all__'

    validators = [
        UniqueTogetherValidator(
            queryset=Favorite.objects.all(),
            fields=('user', 'recipe'),
            message="It is already added to favourite."
        )
    ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['recipe'] = RecipeViewSerializer(instance.recipe).data
        return ret

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            raise serializers.ValidationError(
                "User should be authorised.")
        recipe = Favorite.objects.filter(
            user=request.user, recipe=data["recipe"])
        if recipe:
            raise serializers.ValidationError(
                "It is already added to favourite.")
        return data


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = "__all__"

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            raise serializers.ValidationError(
                "User should be authorised.")
        purchase = data['purchase']
        if Cart.objects.filter(
            user=request.user, purchase=purchase
        ).exists():
            raise serializers.ValidationError(
                'You already added this recipe into the cart'
            )
        return data
