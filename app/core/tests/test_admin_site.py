from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testPass123',
            first_name='admin_first_name',
            last_name='admin_last_name'
        )
        self.user = get_user_model().objects.create(
            email='user@example.com',
            password='testPass123',
            first_name='user_first_name',
            last_name='user_last_name'
        )
        self.client.force_login(self.admin_user)

    def test_users_list_page(self):
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.admin_user.first_name)
        self.assertContains(response, self.admin_user.last_name)
        self.assertContains(response, self.admin_user.email)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.email)

    def test_user_detail_page(self):
        admin_url = reverse('admin:core_user_change',
                            args=[self.admin_user.id])
        admin_response = self.client.get(admin_url)

        user_url = reverse('admin:core_user_change', args=[self.user.id])
        user_response = self.client.get(user_url)

        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(user_response.status_code, 200)

    def test_add_user_page(self):
        url = reverse('admin:core_user_add')
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
