from django.test import TestCase
from django.contrib.auth.models import User


class AuthenticatedBaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
