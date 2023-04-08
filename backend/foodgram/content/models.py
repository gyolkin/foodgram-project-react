from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .validators import validate_hex
from users.models import User


class Tag(models.Model):
    """Цветные теги для рецептов."""
    name = models.CharField(
        max_length=settings.MEDIUM_LENGTH,
        unique=True
    )
    color = models.CharField(
        max_length=settings.HEX_LENGTH,
        validators=[validate_hex],
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты для рецептов."""
    name = models.CharField(
        max_length=settings.MEDIUM_LENGTH
    )
    measurement_unit = models.CharField(
        max_length=settings.SHORT_LENGTH
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""
    name = models.CharField(
        max_length=settings.LONG_LENGTH
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='images'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),)
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(Tag)
    pub_date = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связка для рецептов и игредиентов."""
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='+',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField()


class Favourite(models.Model):
    """Пользовательский список избранного."""
    user = models.ForeignKey(
        User,
        related_name='liker',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='+',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite'
            ),
        )


class ShoppingList(models.Model):
    """Пользовательский шоппинг-лист."""
    user = models.ForeignKey(
        User,
        related_name='shopper',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='+',
        on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list'
            ),
        )

    def __str__(self):
        return f'{self.user.username}: лист покупок'
