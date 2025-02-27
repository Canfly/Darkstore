from django.contrib import admin

from .models import Shipment, Product, SalesChannel, ShipmentChannel, CustomUser, MarketPlaceArticle

admin.site.register(Shipment)
admin.site.register(Product)
admin.site.register(SalesChannel)
admin.site.register(ShipmentChannel)
admin.site.register(CustomUser)
admin.site.register(MarketPlaceArticle)


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product', 'seller', 'shipment_date', 'status')
    list_filter = ('product', 'seller', 'status')


