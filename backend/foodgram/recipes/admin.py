from django.contrib import admin

from .models import Ingredient, Recipe, Subscription, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "pub_date", "author")
    search_fields = ("title", "author")


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "color", "slug")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "unit")
    search_fields = ("title",)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = ("user", "author")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
