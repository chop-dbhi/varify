from django.contrib.auth.models import User
from django.core.cache import cache
from django_rq import get_queue, get_connection
from rq.queue import get_failed_queue
from django.test import TestCase, TransactionTestCase


class AuthenticatedBaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')


class QueueTestCase(TransactionTestCase):
    def setUp(self):
        cache.clear()
        get_queue('variants').empty()
        get_queue('default').empty()
        get_failed_queue(get_connection()).empty()
