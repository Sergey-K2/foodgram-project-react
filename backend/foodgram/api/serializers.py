from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag, User)
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_subscribed"
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=self.context["request"].user, author=obj
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
        )


class RecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField()
    is_in_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_is_in_favorite(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class SubscriptionSerializer(CustomUserSerializer):
    recipes_amount = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes_amount",
            "recipes",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeLimitedSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data

    def get_recipes_amount(self, obj):
        return obj.recipes.count()


class IngredientRecipeSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Минимальное количество ингредиентов = 1"
            ),
        )
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class CreateUpdateRecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Минимальное время приготовления = 1."
            ),
        )
    )

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop("ingredients", None)
        if ingredients is not None:
            instance.ingredients.clear()
        instance = super().update(instance, validated_data)
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    ingredient=Ingredient.objects.get(id=ingredient["id"]),
                    recipe=instance,
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients
            ],
            batch_size=999,
        )
        instance.save()
        return instance

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    ingredient=Ingredient.objects.get(id=ingredient["id"]),
                    recipe=recipe,
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients
            ],
            batch_size=999,
        )
        recipe.save()
        return recipe

    class Meta:
        model = Recipe
        exclude = ("pub_date",)


class RecipeLimitedSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
