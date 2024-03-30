from django.urls import path
from . import views

urlpatterns = [
    path('return-list/', views.return_list, name='return_list'),
    path('generate-barcode/', views.generate_barcode, name='generate_barcode'),
]
