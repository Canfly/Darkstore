from django.shortcuts import render

from .models import Shipment

def shipments(request):
    shipments = Shipment.objects.all()
    return render(request, 'shipments.html', {'shipments': shipments})
