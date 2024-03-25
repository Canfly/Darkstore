#urls.py

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.shipments, name='shipments'),
#    path('home', views.home, name='home'),
#    path('sklad', views.sklad, name='sklad'),
#    path('sign-up', views.sign_up, name='sign_up'),
]
