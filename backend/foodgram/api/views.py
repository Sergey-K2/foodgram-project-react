from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    CustomUser,
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)
from rest_framework import exceptions, filters, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthenticatedOrAuthorOrReadOnly
from .serializers import (
    CreateUpdateRecipeSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    RecipeLimitedSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


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
    permission_classes = (AuthenticatedOrAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "partial_update", "delete"):
            return CreateUpdateRecipeSerializer

        return RecipeSerializer

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)

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
            serializer = RecipeLimitedSerializer(
                recipe, context={"request": request}, many=True
            )
            return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)

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
            serializer = RecipeLimitedSerializer(
                recipe, context={"request": request}, many=True
            )
            return Response(serializer.data)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [element.recipe.id for element in shopping_cart]
        shopping_list = (
            IngredientRecipe.objects.filter(recipe__in=recipes)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        text = "Перечень ингредиентов для рецептов: \n"
        for element in shopping_list:
            ingredient = Ingredient.objects.get(pk=element["ingredient"])
            text += (
                f"{ingredient.name} ({ingredient.measurement_unit})"
                f" - {ingredient.amount}\n"
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
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("^name",)
    filterset_class = IngredientFilter


class UsersSubscriptionViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
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
        queryset = CustomUser.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
    )
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=self.kwargs.get("id"))

        if self.request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError("Подписка уже оформлена.")

            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
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
            return Response("Подписка удалена")
