from django.contrib import admin
from .models import Ingredient, Tag, Recipe, User


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    list_filter = ("author", "title", "tag")


class TagAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "color")


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "unit")
    list_filter = ("title",)


class UserAdmin(admin.ModelAdmin):
    list_filter = ("e-mail", "name")


admin.site.unregister(User)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User, UserAdmin)
