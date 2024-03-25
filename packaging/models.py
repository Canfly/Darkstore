from django.db import models
from django.shortcuts import render
from .models import Client


# ---------тут ничего не сделано, я примерно прикинул какие поля как будут выглядеть и функционировать поля нашей модели--------

class Client(models.Model):
    name = models.CharField(max_length=100, help_text='Имя')
    surname = models.CharField(max_length=100,help_text='Фамилия')
    email = models.EmailField(max_length= 100,help_text='Адрес электронной почты')
    adres = models.CharField(max_length=512, help_text='Адрес')
    inn = models.CharField(max_length=12, help_text='ИНН')
    bank_account = models.FileField(help_text='Расчетный счет')
    BIK = models.CharField(max_lenght=9, help_text='БИК')
    contract = models.FileField(help_text='Договор')

    # Другие поля, такие как email, password и т.д.
    # Метаданные
    class Meta:
        ordering = ['-my_field_name']

    # Methods
    def get_absolute_url(self):
        """Возвращает URL-адрес для доступа к определенному экземпляру MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        """Строка для представления объекта MyModelName (например, в административной панели и т.д.)."""
        return self.my_field_name
# views.py


def client_dashboard(request, client_id):
    client = Client.objects.get(id=client_id)
    # Получение данных о товарах клиента и т.д.
    return render(request, 'client_dashboard.html', {'client': client})


from django.db import models
from django.urls import reverse





# -----------не обращай внимания на код ниже---------------------
# class MyModelName(models.Model):
#     """Типичный класс модели, производный от класса Model."""

#     # Поля
#     my_field_name = models.CharField(max_length=20, help_text='Введите описание поля')
#     # …

#     # Метаданные
#     class Meta:
#         ordering = ['-my_field_name']

#     # Methods
#     def get_absolute_url(self):
#         """Возвращает URL-адрес для доступа к определенному экземпляру MyModelName."""
#         return reverse('model-detail-view', args=[str(self.id)])

#     def __str__(self):
#         """Строка для представления объекта MyModelName (например, в административной панели и т.д.)."""
#         return self.my_field_name
