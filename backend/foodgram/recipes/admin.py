from django.contrib import admin

from .models import Ingredient, Recipe, Subscription, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "text", "pub_date", "author")
    search_fields = ("name", "author")


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = ("user", "author")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
