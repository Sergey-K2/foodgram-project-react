import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ModelSerializer

from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Tag,
    TagRecipe,
    Recipe,
    Subscription,
    User,
    Favorite,
    ShoppingCart,
)


class Base64ImageField(serializers.Field):
    """
    Images are converted from Base64 string
    """

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

    def validate_amount(self, amount):
        if amount not in range(0, 32768):
            return (
                "Количество ингредиента должно быть в интервале от 0 до 32767"
            )
        return amount


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


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

    def update(self, instance, validated_data):
        instance.author = validated_data.get("author", instance.author)
        instance.title = validated_data.get("title", instance.title)
        instance.image = validated_data.get("image", instance.image)
        instance.description = validated_data.get(
            "description", instance.description
        )
        instance.time = validated_data.get("time", instance.time)
        instance.tags.clear()
        instance.tags = self.initial_data.get("tags")
        instance.ingredients.clear()
        instance.ingredients = self.initial_data.get("ingredients")
        instance.save()
        return instance

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe
            )
        for tag in tags:
            current_tag, status = Tag.objects.get_or_create(**tag)
            TagRecipe.objects.create(tag=current_tag, recipe=recipe)
        return recipe

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
