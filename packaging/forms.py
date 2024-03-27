from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    INN = forms.CharField(max_length=100, label='ИНН', required=False)

    ozon_id = forms.CharField(max_length=100, label='OZON_ID', required=False)
    ozon_key = forms.CharField(max_length=100, label='OZON_KEY', required=False)

    sklad_user = forms.CharField(max_length=100, label='SKLAD USER', required=False)
    sklad_pass = forms.CharField(max_length=100, label='SKLAD PASS', required=False)

    def save(self, commit=True):
        user = super().save(commit=False)

        email = self.cleaned_data.get('email', '')
        INN = self.cleaned_data.get('INN', '')
        ozon_id = self.cleaned_data.get('ozon_id', '')
        ozon_key = self.cleaned_data.get('ozon_key', '')
        sklad_user = self.cleaned_data.get('sklad_user', '')
        sklad_pass = self.cleaned_data.get('sklad_pass', '')

        user.first_name = f"{ozon_id}___{ozon_key}"
        user.last_name = f"{sklad_user}___{sklad_pass}"
        user.email = f"{INN}___{email}"
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "ozon_id", "ozon_key", "sklad_user", "sklad_pass"]


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'INN', 'checking_account', 'BIK', 'ozon_client_id', 'ozon_client_key', 'wildberries_api_key',
            'yandex_market_api_key', 'user_type')
