from django.contrib import admin
from .models import Ingredient, Tag, Recipe, User


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    search_filter = (
        "author",
        "title",
    )


class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "color")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("unit",)
    list_filter = ("title",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
