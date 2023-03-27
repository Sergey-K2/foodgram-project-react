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
    ShoppingCard,
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


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class RecipeSerializer(ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="author", many=True, read_only=True
    )
    tag = serializers.SlugRelatedField(
        slug_field="tag", many=True, read_only=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.tag = validated_data.get("tag", instance.tag)
        instance.ingredient = validated_data.get(
            "ingredient", instance.ingredient
        )
        instance.save()
        return instance

    def create(self, validated_data):
        tag = validated_data.pop("tag")
        ingredient = validated_data.pop("ingredient")
        recipe = Recipe.objects.create(**validated_data)
        IngredientRecipe.objects.create(ingredient=ingredient, recipe=recipe)
        TagRecipe.objects.create(tag=tag, recipe=recipe)
        return recipe


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


class FavoriteSerializer(ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
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


class ShoppingCardSerializer(ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = ShoppingCard
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
