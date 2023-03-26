from django.contrib.auth import authenticate
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from content.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from core.seralizers import BasicRecipeSerializer, BasicUserSerializer
from users.models import User


class CustomTokenSerializer(serializers.Serializer):
    """Сериалайзер для работы с токеном."""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Неверный email или пароль.')
        return user


class UserSerializer(BasicUserSerializer):
    """Стандартный сериалайзер для работы с пользователями."""
    class Meta:
        model = User
        fields = BasicUserSerializer.Meta.fields + ('password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SubscribeUserSerializer(BasicUserSerializer):
    """Сериалайзер для работы с пользователями при обработке подписок."""
    recipes = BasicRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = BasicUserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SetPasswordSerializer(serializers.Serializer):
    """Сериалайзер для работы с паролями."""
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(
                'Текущий пароль недействителен.'
            )
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Новый пароль должен быть не короче 8 символов.'
            )
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с тегами."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с ингредиентами в рецептах."""
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredient_data = representation.pop('ingredient')
        for key, value in ingredient_data.items():
            representation[key] = value
        return representation


class RecipeSerializer(BasicRecipeSerializer):
    """Сериалайзер для работы с рецептами."""
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = BasicRecipeSerializer.Meta.fields + (
            'tags', 'text', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favourite.objects.filter(recipe=obj, user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingList.objects.filter(recipes=obj, user=user).exists()
        return False


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с игредиентами
    в рецептах при добавлении нового.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с рецептами при добавлении нового."""
    ingredients = CreateRecipeIngredientSerializer(
        many=True, source='recipe_ingredients', read_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        return recipe
