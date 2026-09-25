from django.contrib import admin
from .models import Cookie, CookieSize, Order, OrderItem


admin.site.register(Cookie)
admin.site.register(CookieSize)
admin.site.register(Order)
admin.site.register(OrderItem)