from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import constraints
from django.db.models.functions import Lower

from users.models import User


class Tag(models.Model):
    '''Model for tags'''
    name = models.CharField(verbose_name='tag', unique=True, max_length=200)
    slug = models.SlugField(verbose_name='slug', max_length=200, unique=True)
    color = models.CharField(verbose_name='color', max_length=7)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    '''Model for ingredients'''
    name = models.CharField(
        verbose_name='name_ingredient',
        max_length=200)
    measurement_unit = models.CharField(
        verbose_name='type of measurment', max_length=200)

    class Meta:
        ordering = [Lower('name'), ]
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [constraints.UniqueConstraint(
            fields=['name', 'measurement_unit'], name='prevention doubling')]

    def __str__(self):
        return f'{self.name}, ({self.measurement_unit})'


class RecipeIngredient(models.Model):
    '''Model that connected Ingredient whith Recipe'''
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='id_ingredient',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    recipe = models.ForeignKey(
        'Recipe', verbose_name='id_recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    amount = models.PositiveIntegerField(
        verbose_name='quantity of ingredient',
        validators=[
            MinValueValidator(0, 'The amount must be more than zero.'),
            MaxValueValidator(10000, 'The amount must be less than 10000.')
        ])

    class Meta:
        verbose_name = 'RecipeIngredient'
        verbose_name_plural = 'RecipeIngredients'


class Recipe(models.Model):
    '''Model for Recipe'''
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='ingredients',
        through=RecipeIngredient)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes')
    tags = models.ManyToManyField(
        Tag, verbose_name='tag')
    image = models.ImageField(
        verbose_name='image', upload_to='recipes/')
    name = models.CharField(
        verbose_name='name of dish', unique=False,
        max_length=200)
    text = models.TextField(
        verbose_name='description of the cooking process')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='time of cooking',
        validators=[
            MinValueValidator(1, 'The cooking_time must be more than zero.'),
            MaxValueValidator(1000, 'The cooking_time must be less than 1000.')
        ])
    pud_date = models.DateTimeField(
        verbose_name='date of publication', default=datetime.now,)

    STRING_METHOD_MESSAGE = (
        'name: {name}, author:{author}'
    )

    class Meta:
        ordering = ['-pud_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return self.STRING_METHOD_MESSAGE.format(
            name=self.name,
            author=self.author
        )


'''class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tag')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)'''


class Cart(models.Model):
    purchase = models.ForeignKey(
        Recipe, verbose_name='list of purchases',
        related_name='purchases',
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name='user',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        constraints = [constraints.UniqueConstraint(
            fields=['user', 'purchase'], name='prevention doubling in a cart')]

    def __str__(self) -> str:
        return f"{self.user} want to buy {self.purchase}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User, verbose_name='user', on_delete=models.CASCADE,
        related_name='liker')
    recipe = models.ForeignKey(
        Recipe, verbose_name='recipe', on_delete=models.CASCADE,
        related_name='favorite_rec')

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [constraints.UniqueConstraint(
            fields=['user', 'recipe'], name='it is already in my favorite')]

    def __str__(self) -> str:
        return f"{self.user} like {self.recipe}"


class Follow(models.Model):
    user = models.ForeignKey(
        User, verbose_name='user', on_delete=models.CASCADE,
        related_name='follower')
    author = models.ForeignKey(
        User, verbose_name='author of the recipe', on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        constraints = [constraints.UniqueConstraint(
            fields=['user', 'author'], name='unique_subscription')]

    def __str__(self) -> str:
        return f"{self.user} follows {self.author}"
