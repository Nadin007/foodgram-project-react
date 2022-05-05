from django.test import Client, TestCase

try:
    from recipe_features.models import Ingredient
except ImportError:
    assert False, 'Ingredient model does not find!'

try:
    from recipe_features.models import Recipe
except ImportError:
    assert False, 'Ingredient model does not find!'

try:
    from users.models import User
except ImportError:
    assert False, 'User model does not find!'

try:
    from recipe_features.models import RecipeIngredient
except ImportError:
    assert False, 'RecipeIngredient model does not find!'


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ingredient_1 = Ingredient.objects.create(
            name='Cottage cheese',
            measurement_unit='gram'
        )
        cls.ingredient_2 = Ingredient.objects.create(
            name='Flour',
            measurement_unit='gram'
        )
        cls.ingredient_3 = Ingredient.objects.create(
            name='Egg',
            measurement_unit='pieces'
        )
        cls.user_1 = User.objects.create(
            first_name="Dima", last_name="Smirnov", username="Dimon",
            email="dimon@gmail.com", password='123eddws')

        cls.resipe_1 = Recipe.objects.create(
            ingredients=[
                {'id': Ingredient.objects.filter(
                    name=cls.ingredient_1.name)[0],
                 'amount': 222},
                {'id': Ingredient.objects.filter(
                    name=cls.ingredient_2.name)[0],
                 'amount': 333},
                {'id': Ingredient.objects.filter(
                    name=cls.ingredient_3.name)[0],
                 'amount': 1}, ],
            author=User.objects.filter(user=cls.user_1)[0].id,
            name='Recipe 1',
            text='Description of rhe recipe 1.',
            cooking_time=40
        )
        cls.ingredient_amount_1 = RecipeIngredient.objects.create(
            ingredient=Recipe.object.filter()[0][0],
            recipe=Recipe.object.filter(),
            amount=Recipe.objects.filter(),)

    @classmethod
    def tearDownClass(cls) -> None:
        User.objects.all().delete()
        Recipe.objects.all().delete()
        RecipeIngredient.objects.all().delete()
        Ingredient.objects.all().delete()
        print('tearDownClass successfully completed')

    def setUp(self):
        self.guest_client = Client()

    def test_url_for_availability_for_all_visitors(self):
        """The pages "/recipes", "/about/author/", "/about/tech/",
        "/auth/signup/", "/username/", "/username/post_id/"
        are available to any user."""

        response = self.guest_client.get('/api/recipes/')
        print(response)
        self.assertEqual(response.status_code, 200)
