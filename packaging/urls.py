# urls.py

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('shipments/', views.shipments, name='shipments'),
    path('products/', views.products, name='products'),
    path("sync/", views.sync_products, name="sync_products"),
    path('stocks/', views.sync_stocks, name="sync_stocks"),
    path('register/', views.register, name='register'),
    #path('login/', views.login, name='login'),

    #    path('home', views.home, name='home'),
    #    path('sklad', views.sklad, name='sklad'),
    #    path('sign-up', views.sign_up, name='sign_up'),
]
