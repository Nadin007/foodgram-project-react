def format_ingredient(ingredient):
    name = ingredient['recipe_ingredients__name']
    measure = ingredient['recipe_ingredients__measurement_unit']
    amount = ingredient['amount']
    return f'{name} ({measure}) - {amount}'
