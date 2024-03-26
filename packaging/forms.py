from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'INN', 'checking_account', 'BIK', 'ozon_client_id', 'ozon_client_key', 'wildberries_api_key', 'yandex_market_api_key', 'user_type')
