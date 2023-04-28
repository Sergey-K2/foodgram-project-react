import base64

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag, User)
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator


class Base64ImageField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


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


class RecipeSerializer(ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="author", many=True, read_only=True
    )
    tag = TagSerializer(many=True)
    ingredient = IngredientSerializer(many=True)
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


class SubscriptionSerializer(ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=["user", "following"],
            )
        ]

    def validate_following(self, following):
        if following == self.context["request"].user:
            raise serializers.ValidationError("User и Following одинаковы")
        return following


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


class CustomUserSerializer(UserSerializer):
    is_following = serializers.SerializerMethodField(read_only=True)

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

    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=self.context["request"].user, author=obj
        ).exists()


class CurrentUserDefaultId(object):
    requires_context = True

    def __call__(self, serializer_instance=None):
        if serializer_instance is not None:
            self.user_id = serializer_instance.context["request"].user.id
            return self.user_id


class IngredientRecipeSerializer(ModelSerializer):
    id = serializers.SerializerMethodField(method_name="get_id")
    name = serializers.SerializerMethodField(method_name="get_name")
    measurement_unit = serializers.SerializerMethodField(
        method_name="get_measurement_unit"
    )

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")

    def validate_amount(self, amount):
        if (
            amount < settings.INGREDIENT_LOWER_LIMIT
            or amount > settings.INGREDIENT_UPPER_LIMIT
        ):
            return (
                "Количество ингредиента должно"
                "быть в интервале от 0 до 32767"
            )
        return amount


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
        instance.author = validated_data.get("author", instance.author)
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.tags.clear()
        instance.tags = self.initial_data.get("tags")
        instance.ingredients.clear()
        instance.ingredients = self.initial_data.get("ingredient")
        instance.save()
        return instance

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredient")
        recipe = Recipe.objects.create(**validated_data)
        Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    ingredient=ingredients.get("id"),
                    recipe=recipe,
                    amount=ingredients.get("amount"),
                    measurement_unit=ingredients.get("measurement_unit"),
                )
                for ingredient in ingredients
            ],
            batch_size=999,
        )
        recipe.save()
        return recipe


class CreateUpdateIngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1, message="Минимальное количество ингредиентов = 1"
            ),
        )
    )

    class Meta:
        model = Ingredient
        fields = ("id", "amount")
