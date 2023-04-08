from io import BytesIO

from django.http import FileResponse


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
