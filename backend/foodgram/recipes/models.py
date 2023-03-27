from django.contrib.auth import get_user_model
from django.db import models

CHOICES_UNITS_OF_MEASUREMENT = (
    ("Кг", "Килограмм"),
    ("Гр", "Грамм"),
    ("Мг", "Миллиграм"),
    ("Шт", "Штук"),
)

User = get_user_model()


class Tag(models.Model):
    title = models.CharField(verbose_name="Название", unique=True)
    slug = models.SlugField(verbose_name="Идентификатор тэга", unique=True)
    color = models.CharField(max_length=6, unique=True)


class Ingredient(models.Model):
    title = models.CharField(verbose_name="Название", unique=True)
    amount = models.IntegerField(verbose_name="Количество")
    unit = models.CharField(
        verbose_name="Единицы измерения", choices=CHOICES_UNITS_OF_MEASUREMENT
    )


class TagRecipe(models.Model):
    tag = models.ForeignKey(on_delete=models.CASCADE)
    recipe = models.ForeignKey(on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(on_delete=models.CASCADE)
    recipe = models.ForeignKey(on_delete=models.CASCADE)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор",
    )
    title = models.CharField(verbose_name="Название", max_length=200)
    image = models.ImageField(
        verbose_name="Картинка", upload_to="recipes/images/"
    )
    description = models.TextField(verbose_name="Описание")
    ingredient = models.ManyToManyField(
        Ingredient,
        on_delete=models.SET_NULL,
        related_name="recipe",
        verbose_name="Ингридиент",
        through=IngredientRecipe,
    )
    tag = models.ManyToManyField(
        Tag,
        on_delete=models.SET_NULL,
        related_name="recipe",
        verbose_name="Тэг",
        through=TagRecipe,
    )
    time = models.TimeField(verbose_name="Время приготовления")
    is_in_favorite = models.BooleanField(verbose_name="В избранном?")
    is_in_shopping_cart = models.BooleanField(verbose_name="В списке покупок?")

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
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
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
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


class ShoppingCard(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
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
