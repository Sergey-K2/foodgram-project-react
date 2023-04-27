from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Subscription, Tag, User)
from rest_framework import exceptions, filters, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .permissions import AuthenticatedOrAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)


class ListRetrieveViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    pass


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    pass


class CreateDeleteViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    pass


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthenticatedOrAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "DELETE":
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError("Рецепт не в избранном!")
            get_object_or_404(Favorite, user=user, recipe=recipe).delete()
            return Response()

        if self.request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    "Рецепт уже добавлен в избранное!"
                )

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(
                recipe, context={"request": request}, many=True
            )
            return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == "DELETE":
            if not ShoppingCart.objects.filter(
                user=user, recipe=recipe
            ).exists():
                raise exceptions.ValidationError("Рецепт не в списке покупок!")
            get_object_or_404(ShoppingCart, user=user, recipe=recipe).delete()
            return Response()

        if self.request.method == "POST":
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    "Рецепт уже добавлен в список покупок!"
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(
                recipe, context={"request": request}, many=True
            )
            return Response(serializer.data)

    @action(
        detail=True, methods=["get"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [element.recipe.id for element in shopping_cart]
        shopping_list = (
            IngredientRecipe.objects.filter(recipe__in=recipes)
            .values("ingredient")
            .annotate(amount=Sum("amount"))
        )
        text = "Перечень ингредиентов для рецептов: \n"
        for element in shopping_list:
            ingredient = Ingredient.objects.get(pk=element["ingredient"])
            text += (
                f"{ingredient.title} ({ingredient.unit}) - {element.amount}\n"
            )
        return HttpResponse(
            text,
            content_type="text/plain",
            headers={
                "Content-Disposition": "attachment; filename=shopping-list.txt"
            },
        )


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UsersSubscriptionViewSet(UserViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username", "user__username")
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=["get"],
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
    )
    def subscribe(self, request, pk=None):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)

        if self.request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError("Подписка уже оформлена.")

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data)

        if self.request.method == "DELETE":
            if not Subscription.objects.filter(
                user=user, author=author
            ).exists():
                raise exceptions.ValidationError("Подписки не существует")
            subscription = get_object_or_404(
                Subscription, user=user, author=author
            )
            subscription.delete()
