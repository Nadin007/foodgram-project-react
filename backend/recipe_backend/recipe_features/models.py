from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import constraints

from users.models import User


class Tag(models.Model):
    '''Model for tags'''
    name = models.CharField(verbose_name='tag', unique=True, max_length=50)
    slug = models.SlugField(verbose_name='slug', max_length=50, unique=True)
    color = models.CharField(verbose_name='color', max_length=50, unique=False)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='name of ingredient', unique=True,
        max_length=200)
    measurement_unit = models.CharField(
        verbose_name='type of measurment', null=False, max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"
        constraints = [constraints.UniqueConstraint(
            fields=['name', 'measurement_unit'], name='prevention doubling')]

    def __str__(self):
        return f'{self.ingredient}, ({self.measure})'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='id of ingredient',
        on_delete=models.CASCADE,
        related_name="ingredient"
    )
    recipe = models.ForeignKey(
        "Recipe", verbose_name='id of recipe',
        on_delete=models.CASCADE,
        related_name="recipe",
        null=False,)
    amount = models.PositiveIntegerField(
        verbose_name='quantity of ingredient',
        blank=False,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10000)
        ])


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='ingredients',
        through=RecipeIngredient, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author_recipe')
    tags = models.ManyToManyField(
        Tag, verbose_name='tag', through='TagRecipe', blank=False)
    image = models.ImageField(
        verbose_name='image', upload_to='recipes/', blank=False, null=False)
    name = models.CharField(
        verbose_name='name of dish', unique=False,
        blank=False, null=False, max_length=200)
    text = models.TextField(
        verbose_name='description of the cooking process',
        blank=False, null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='time of cooking', blank=False, null=False,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1000)
        ])
    pud_date = models.DateTimeField(
        verbose_name='date of publication', default=datetime.now,)

    STRING_METHOD_MESSAGE = (
        'name: {name}, author:{author}'
    )

    class Meta:
        ordering = ['pud_date']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return self.STRING_METHOD_MESSAGE.format(
            name=self.name,
            author=self.author
        )


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tag')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Cart(models.Model):
    purchase = models.ForeignKey(
        Recipe, verbose_name='list of purchases',
        blank=False, related_name='purchases',
        on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name='user', blank=False,
        on_delete=models.CASCADE
    )

    class Meta:
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
        constraints = [constraints.UniqueConstraint(
            fields=['user', 'author'], name='unique_subscription')]

    def __str__(self) -> str:
        return f"{self.user} follows {self.author}"


class Comment(models.Model):
    recipe = models.ForeignKey(
        Recipe, verbose_name='recipe', on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        User, verbose_name='user', on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField(verbose_name='comment', max_length=500)
    created = models.DateTimeField(
        verbose_name='date published', auto_now_add=True)
    path = ArrayField(models.IntegerField())

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:15]

    def getoffset(self):
        level = len(self.path) - 1
        if level > 5:
            level = 5
        return level
