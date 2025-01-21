from django.contrib import admin
from .models import *
# Register your models here.

class details(admin.ModelAdmin):
    list_display=('name','price','image')

admin.site.register(Catagory)
admin.site.register(Customer)
admin.site.register(Product,details)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Coupon)