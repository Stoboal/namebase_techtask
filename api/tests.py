from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class APITestView(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test!12354')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.test_name = 'Andrew'
        self.test_country = 'GB'


    def test_get_name_stats_no_param(self):
        url = reverse('name-stats')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_name_stats_with_param(self):
        url = reverse('name-stats')
        response = self.client.get(f'{url}?name={self.test_name}', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_popular_names_by_country_no_param(self):
        url = reverse('popular-names')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_popular_names_by_country_with_param(self):
        url = reverse('popular-names')
        response = self.client.get(f'{url}?country={self.test_country}', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
