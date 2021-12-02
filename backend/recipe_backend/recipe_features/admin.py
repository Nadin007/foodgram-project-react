import os

from django.contrib import admin
from django.utils.safestring import mark_safe
from recipe_backend.settings import BASE_DIR

from .models import (Cart, Favorite, Follow, Ingredient, Recipe,
                     RecipeIngredient, Tag, TagRecipe)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color", "id")
    search_fields = ("slug",)
    ordering = ('name', )
    list_filter = ('slug', 'color')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ("tag", "recipe")
    search_fields = ("recipe",)
    ordering = ("recipe",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "recipe", "amount")
    search_fields = ("recipe",)
    ordering = ("recipe",)


class RecipeTagInline(admin.TabularInline):
    model = TagRecipe


class RecipeIngridienceInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = (
        'image', 'author', 'name', 'text', 'cooking_time')
    list_display = (
        'get_image', 'author', 'name', 'text', 'cooking_time',
        'get_favorited')
    search_fields = ("name",)
    ordering = ("name",)
    inlines = (RecipeTagInline, RecipeIngridienceInline)
    list_filter = ('name', 'author', 'tags')

    def get_ing(self):
        if self.image:
            return self.image.url
        return os.path.join(BASE_DIR, 'media/avatars/default-1.png')

    @admin.display()
    def get_image(self, instance):
        return mark_safe(
            '<img src="%s" width="50" height="50" />' % instance.image.url)

    @admin.display(description='Number of likes')
    def get_favorited(self, instance):
        return Favorite.objects.filter(recipe=instance).count()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "purchase")
    search_fields = ("user",)
    ordering = ("user",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user", "recipe")
    ordering = ("user",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("user", "author")
    ordering = ("user",)
