def format_ingredient(ingredient):
    name = ingredient['ingredient__name']
    measure = ingredient['ingredient__measurement_unit']
    amount = ingredient['amount']
    return f'{name} ({measure}) - {amount}'
