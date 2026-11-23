from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class AuthFlowTests(TestCase):
    password = 'S3cure-Passw0rd!'

    def make_user(self):
        return User.objects.create_user(
            'kenji', 'kenji@example.com', self.password
        )

    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(reverse('signup'), {
            'username': 'yuki',
            'email': 'Yuki@Example.com',
            'password1': self.password,
            'password2': self.password,
        })
        self.assertRedirects(response, reverse('flashcards'))
        user = User.objects.get(username='yuki')
        self.assertEqual(user.email, 'yuki@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_rejects_duplicate_email(self):
        self.make_user()
        response = self.client.post(reverse('signup'), {
            'username': 'other',
            'email': 'KENJI@example.com',
            'password1': self.password,
            'password2': self.password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='other').exists())

    def test_flashcards_require_login(self):
        response = self.client.get(reverse('flashcards'))
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('flashcards')
        )

    def test_login_and_logout(self):
        self.make_user()
        response = self.client.post(reverse('login'), {
            'username': 'kenji', 'password': self.password,
        })
        self.assertRedirects(response, reverse('flashcards'))
        self.assertEqual(self.client.get(reverse('flashcards')).status_code, 200)

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_wrong_password_rejected(self):
        self.make_user()
        response = self.client.post(reverse('login'), {
            'username': 'kenji', 'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_password_reset_sends_email(self):
        self.make_user()
        response = self.client.post(
            reverse('password_reset'), {'email': 'kenji@example.com'}
        )
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/reset/', mail.outbox[0].body)

    def test_auth_pages_render(self):
        for name in ('login', 'signup', 'password_reset'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        self.make_user()
        self.client.login(username='kenji', password=self.password)
        self.assertEqual(
            self.client.get(reverse('password_change')).status_code, 200
        )
