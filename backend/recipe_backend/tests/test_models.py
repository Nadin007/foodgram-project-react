from django.test import TestCase

from recipe_features.models import Ingredient


class TestFeathuresModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ingredient = Ingredient.objects.create(
            name='Carrot',
            measurement_unit='pieces'
        )

    def test_name_label(self):
        ingredient = TestFeathuresModel.ingredient
        verbose_name = ingredient._meta.get_field('name').verbose_name
        self.assertEqual(verbose_name, 'name_ingredient')

    def test_measurement_unit_label(self):
        ingredient = TestFeathuresModel.ingredient
        verbose_name = ingredient._meta.get_field(
            'measurement_unit').verbose_name
        self.assertEqual(verbose_name, 'type of measurment')

    def test_object_name_is_title_fild(self):
        ingredient = TestFeathuresModel.ingredient
        name_self = ingredient.__str__()
        self.assertEqual(name_self, 'carrot, (pieces)')
