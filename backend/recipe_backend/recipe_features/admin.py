from django.contrib import admin

from .models import (
    Ingredient, Tag, Recipe, TagRecipe, RecipeIngredient)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color")
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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = (
        'image', 'author', 'name', 'text', 'cooking_time', )
    list_display = (
        'image', 'author', 'name', 'text', 'cooking_time',
        )
    search_fields = ("name",)
    ordering = ("name",)

    """def get_queryset(self, request):
        print('jvndvijdvibfdvb')
        qs = super().get_queryset(request)
        qs.get('tags')
        print(request, qs)
        return qs.prefetch_related('tag')

    def get_tags(self, obj):
        return "\n".join([p.tags for p in obj.tag.all()])"""
