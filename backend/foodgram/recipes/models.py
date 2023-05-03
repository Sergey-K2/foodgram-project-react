from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]
    email = models.EmailField(
        "email address",
        unique=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название", unique=True, max_length=100
    )
    slug = models.SlugField(verbose_name="Идентификатор тэга", unique=True)
    color = models.CharField(max_length=7, unique=True)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"


class Ingredient(models.Model):
    name = models.CharField(verbose_name="Название", max_length=100)
    measurement_unit = models.CharField(
        verbose_name="Единицы измерения",
        max_length=100,
    )

    class Meta:
        ordering = ("-name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_recipe",
            ),
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    name = models.CharField(verbose_name="Название", max_length=200)
    image = models.ImageField(
        verbose_name="Картинка", upload_to="recipes/images/"
    )
    text = models.TextField(
        verbose_name="Описание", help_text="Описание рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        related_name="recipes",
        verbose_name="Ингридиент",
    )
    tags = models.ManyToManyField(
        Tag,
        through="TagRecipe",
        related_name="recipe",
        verbose_name="Тег",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления"
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество", null=True
    )


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="User can't subscribe on himself",
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return (
            f"Подписка пользователя {self.user.username}"
            f" на автора {self.author.username}"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )
    added = models.DateTimeField("Дата и время публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite_recipe"
            ),
        )

    def __str__(self):
        return (
            f"Рецепт {self.recipe} в списке избранного"
            f"пользователя {self.user.username}."
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="added_to_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт в списке покупок",
    )
    added = models.DateTimeField("Дата и время публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_list_recipe"
            ),
        )

    def __str__(self):
        return (
            f"Рецепт {self.recipe} в корзине"
            f"пользователя {self.user.username}."
        )
