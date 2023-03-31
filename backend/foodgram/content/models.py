from django.core.validators import MinValueValidator
from django.db import models

from users.models import User
from .validators import validate_hex


class Tag(models.Model):
    """Цветные теги для рецептов."""
    name = models.CharField(
        max_length=100,
        unique=True
    )
    color = models.CharField(
        max_length=7,
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
        max_length=100
    )
    measurement_unit = models.CharField(
        max_length=10
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""
    name = models.CharField(
        max_length=200
    )
    text = models.TextField(
        max_length=1000
    )
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
