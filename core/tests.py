from django.test import TestCase

# Create your tests here.
from unittest.mock import patch

from .models import User


class UserCreationEmailTests(TestCase):
    @patch("core.signals.send_mail")
    def test_creation_includes_temporary_password(self, send_mail):
        user = User(
            username="new-user",
            email="new-user@example.com",
        )
        user.set_password("password")
        user._creation_password = "password"
        user.save()

        self.assertIn("Your password is password.", send_mail.call_args.args[1])

    @patch("core.signals.send_mail")
    def test_creation_sends_registration_email(self, send_mail):
        user = User.objects.create_user(
            username="new-user",
            email="new-user@example.com",
            password="password",
        )

        send_mail.assert_called_once()
        self.assertEqual(send_mail.call_args.args[3], [user.email])
        self.assertIn(user.username, send_mail.call_args.args[1])

    @patch("core.signals.send_mail")
    def test_update_does_not_send_registration_email(self, send_mail):
        user = User.objects.create_user(
            username="existing-user",
            email="existing-user@example.com",
            password="password",
        )
        send_mail.reset_mock()

        user.first_name = "Updated"
        user.save()

        send_mail.assert_not_called()
