from django.contrib import admin

from .models import Shipment, Product, Seller, User, SalesChannel, ShipmentChannel, CustomUser

admin.site.register(Shipment)
admin.site.register(Product)
admin.site.register(Seller)
admin.site.register(User)
admin.site.register(SalesChannel)
admin.site.register(ShipmentChannel)
admin.site.register(CustomUser)



class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product', 'seller', 'shipment_date', 'status')
    list_filter = ('product', 'seller', 'status')


