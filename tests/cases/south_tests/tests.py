from django.test import TestCase
from django.test.utils import override_settings


@override_settings(SOUTH_TESTS_MIGRATE=True)
class SouthTests(TestCase):
    def test(self):
        self.assertTrue(True)
