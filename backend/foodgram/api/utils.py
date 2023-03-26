from io import BytesIO

from django.http import FileResponse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User


def file_create(recipes):
    """Функция для создания файла со всеми ингредиентами."""
    aggregated_ingredients = {}
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            key = (recipe_ingredient.ingredient.name, recipe_ingredient.ingredient.measurement_unit)
            if key in aggregated_ingredients:
                aggregated_ingredients[key] += recipe_ingredient.amount
            else:
                aggregated_ingredients[key] = recipe_ingredient.amount

    content = "\n".join([f"{ingredient[0]} {amount} {ingredient[1]}" for ingredient, amount in aggregated_ingredients.items()])
    byte_content = content.encode('utf-8')
    response = FileResponse(BytesIO(byte_content), as_attachment=True, filename='shopping_list.txt')
    response['Content-Type'] = 'text/plain'
    return response


def get_user_from_access_token(access_token):
    """Функция для получения пользователя из access token."""
    try:
        token = AccessToken(access_token)
        user_id = token.get('user_id')
        if user_id is None:
            return None
        return User.objects.filter(id=user_id).first()
    except TokenError:
        return None
