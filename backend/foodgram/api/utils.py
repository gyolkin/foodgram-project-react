from io import BytesIO

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from content.models import Recipe


def file_create(recipes):
    """Функция для создания файла со всеми ингредиентами."""
    aggregated_ingredients = {}
    for recipe in recipes:
        for recipe_ingredient in recipe.recipe_ingredients.all():
            key = (
                recipe_ingredient.ingredient.name,
                recipe_ingredient.ingredient.measurement_unit
            )
            if key in aggregated_ingredients:
                aggregated_ingredients[key] += recipe_ingredient.amount
            else:
                aggregated_ingredients[key] = recipe_ingredient.amount

    content = "\n".join(
        [f"{ingredient[0]} {amount} {ingredient[1]}"
         for ingredient, amount in aggregated_ingredients.items()]
    )
    byte_content = content.encode('utf-8')
    response = FileResponse(
        BytesIO(byte_content),
        as_attachment=True,
        filename='shopping_list.txt'
    )
    response['Content-Type'] = 'text/plain'
    return response


def create_obj(request, pk, model, serializer):
    """Функция для создания объекта, связанного с рецептами"""
    recipe = get_object_or_404(Recipe, id=pk)
    _, created = model.objects.get_or_create(
        user=request.user, recipe=recipe
    )
    if not created:
        return Response(
            {'errors': 'Вы уже выполнили это действие.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    serializer = serializer(
        recipe, context={'request': request}
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_obj(request, pk, model):
    """Функция для удаления объекта, связанного с рецептами"""
    recipe = get_object_or_404(Recipe, id=pk)
    obj = model.objects.filter(
        user=request.user, recipe=recipe).first()
    if not obj:
        return Response(
            {'errors': 'Невозможно выполнить это действие.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
