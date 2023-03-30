from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Tag(models.Model):
    title = models.CharField(
        verbose_name="Название", unique=True, max_length=100
    )
    slug = models.SlugField(verbose_name="Идентификатор тэга", unique=True)
    color = models.CharField(max_length=6, unique=True)

    class Meta:
        ordering = ("-title",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"


class Ingredient(models.Model):
    CHOICES_UNITS_OF_MEASUREMENT = (
        ("Кг", "Килограмм"),
        ("Гр", "Грамм"),
        ("Мг", "Миллиграм"),
        ("Шт", "Штук"),
    )

    title = models.CharField(
        verbose_name="Название", unique=True, max_length=100
    )
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")
    unit = models.CharField(
        verbose_name="Единицы измерения",
        choices=CHOICES_UNITS_OF_MEASUREMENT,
        max_length=100,
    )

    class Meta:
        ordering = ("-title",)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    title = models.CharField(verbose_name="Название", max_length=200)
    image = models.ImageField(
        verbose_name="Картинка", upload_to="recipes/images/"
    )
    description = models.TextField(verbose_name="Описание")
    ingredient = models.ManyToManyField(
        Ingredient,
        related_name="recipe",
        verbose_name="Ингридиент",
    )
    tag = models.ManyToManyField(
        Tag,
        related_name="recipe",
        verbose_name="Тэг",
    )
    time = models.PositiveSmallIntegerField(verbose_name="Время приготовления")
    is_in_favorite = models.BooleanField(verbose_name="В избранном?")
    is_in_shopping_cart = models.BooleanField(verbose_name="В списке покупок?")

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


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
        related_name="follow",
        verbose_name="Подписчик",
    )
    Recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="follow",
        verbose_name="Автор",
    )
    added = models.DateTimeField("Дата и время публикации", auto_now_add=True)

    class Meta:
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
        related_name="foll",
        verbose_name="Подписчик",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="foll",
        verbose_name="Автор",
    )
    added = models.DateTimeField("Дата и время публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return (
            f"Подписка пользователя {self.user.username}"
            f" на автора {self.author.username}"
        )
