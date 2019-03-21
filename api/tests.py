from django.urls import reverse
from rest_framework.test import APITestCase

from api.models import ApiUser, Message


class ListCreateUsersTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('api:users')

    def test_create_user(self):
        response = self.client.post(self.url, {'username': 'sam'})
        self.assertEqual(201, response.status_code)

    def test_create_duplicate_user(self):
        ApiUser.objects.create(username='sam')
        response = self.client.post(self.url, {'username': 'SAM'})
        self.assertEqual(400, response.status_code)

    def test_create_numeric_user(self):
        response = self.client.post(self.url, {'username': '1234'})
        self.assertEqual(400, response.status_code)

    def test_list_users(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


class ListCreateMessagesTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('api:messages')
        user = ApiUser.objects.create(username='sam')
        self.user_id = user.id

    def test_create_message(self):
        data = {'to_user': self.user_id, 'content': 'test message'}
        response = self.client.post(self.url, data)
        self.assertEqual(201, response.status_code)

    def test_list_messages(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


class ViewDeleteMessageTestCase(APITestCase):

    def setUp(self):
        message = Message.objects.create(content='test message')
        self.url = reverse('api:messages_id', kwargs={'id': message.id})

    def test_view_message(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_delete_message(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)


class ListCreateUserMessageTestCase(APITestCase):

    def setUp(self):
        self.username = 'sam'
        self.url = reverse('api:messages_user', kwargs={'username': self.username})
        user = ApiUser.objects.create(username=self.username)
        Message.objects.create(content='test message', to_user=user)

    def test_list_user_messages(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_create_user_message(self):
        response = self.client.post(self.url, {'content': 'another message'})
        self.assertEqual(201, response.status_code)


class MessageBatchReadDeleteTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('api:messages_batch')
        Message.objects.create(content='first message')
        Message.objects.create(content='second message')
        queryset = Message.objects.all()
        self.message_ids = [str(message.id) for message in queryset]
        self.message_id_string = ','.join(self.message_ids)

    def test_delete_messages(self):
        data = {'action': 'delete', 'message_ids': self.message_id_string}
        response = self.client.patch(self.url, data)
        self.assertEqual(204, response.status_code)
        queryset = Message.objects.all()
        self.assertEqual(len(queryset), 0)

    def test_read_messages(self):
        data = {'action': 'mark_as_read', 'message_ids': self.message_id_string}
        response = self.client.patch(self.url, data)
        self.assertEqual(200, response.status_code)
        queryset = Message.objects.filter(fetched=False)
        self.assertEqual(len(queryset), 0)
