from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import BooleanField
from .models import User
from euromammals.functions_admin import CsvImportForm


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)


class UserImportForm(CsvImportForm):
    is_staff = BooleanField(initial=False, required=False)
    is_superuser = BooleanField(initial=False, required=False)
