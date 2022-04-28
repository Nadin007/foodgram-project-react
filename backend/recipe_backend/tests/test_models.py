from django.test import TestCase, Client
from django.db.utils import IntegrityError

try:
    from recipe_features.models import Ingredient
except ImportError:
    assert False, 'Ingredient model does not find!'

try:
    from users.models import User
except ImportError:
    assert False, 'User model does not find!'


class TestUserModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User.objects.create(
            first_name="Dima", last_name="Smirnov", username="Dimon",
            email="dimon@gmail.com", password='123eddws')
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()
        print('tearDownClass выполнен')

    def setUp(self) -> None:
        self.guest_client = Client()
        self.visitor = TestUserModel.user

    def test_label_name(self):
        '''Vervose_name for fields.'''
        field_verboses = {
            'username': 'username',
            'first_name': 'first name',
            'last_name': 'last name',
            'email': 'email address',
            'role': 'user`s role',
            'avatar': 'avatar',
            'date_joined': 'date joined',
            'password': 'password',
        }
        for field, expected_values in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.visitor._meta.get_field(field).verbose_name,
                    expected_values
                )

    def test_help_text(self):
        '''Help test for fields.'''
        field_help = {
            'username': 'Please enter up to 150 characters',
            'first_name': '',
            'last_name': '',
            'email': '',
            'role': '',
            'avatar': 'Choose the avatar',
            'date_joined': '',
            'password': '',
        }
        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.visitor._meta.get_field(field).help_text,
                    expected_value
                )

    def test_double_username(self):
        '''Check unique username'''
        self.assertRaises(
            IntegrityError,
            lambda: User.objects.create(
                first_name="Dima", last_name="Smirnov", username="Dimon",
                email="dimon2@gmail.com", password='123eddws')
        )

    def test_correct(self):
        user_2 = User.objects.create(
            last_name="Juan", username="Ian_1",
            email="ian@gmail.com", password='1111111')
        self.assertEqual(user_2.first_name, '')


class TestFeathuresModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.ingredient = Ingredient.objects.create(
            name='Carrot',
            measurement_unit='pieces'
        )

    @classmethod
    def tearDownClass(cls) -> str:
        User.objects.all().delete()
        cls.ingredient.delete
        print('tearDownClass выполнен')

    def test_name_label(self):
        '''Vervose_name for fields.'''
        ingredient = TestFeathuresModel.ingredient
        field_verboses = {
            'name': 'name_ingredient',
            'measurement_unit': 'type of measurment',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    ingredient._meta.get_field(field).verbose_name,
                    expected_value)

    def test_object_name_is_title_fild(self):
        ingredient = TestFeathuresModel.ingredient
        name_self = ingredient.__str__()
        self.assertEqual(name_self, 'Carrot, (pieces)')
