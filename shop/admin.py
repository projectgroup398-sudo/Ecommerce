from django.contrib import admin

from .models import Product ,CartItem,UserAddress,Order,Ecurrency,TransactionHistory

admin.site.register(Product)
admin.site.register(UserAddress)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Ecurrency)
admin.site.register(TransactionHistory)