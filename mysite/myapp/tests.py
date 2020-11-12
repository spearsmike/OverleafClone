from django.test import TestCase
from django.contrib.auth.models import User
from . import models

class DocumentTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user('Arnold', 'schwarzenegger@mail.com', 'illbeback')
        user.save()
        user_instance = User.objects.get(id=1)
        models.DocumentModel.objects.create(book="lion", author=user)
