#urls.py

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.shipments, name='shipments'),
    path("sync/", views.sync_products, name="sync_products"),
    path('register/', views.register, name='register'),

#    path('home', views.home, name='home'),
#    path('sklad', views.sklad, name='sklad'),
#    path('sign-up', views.sign_up, name='sign_up'),
]
