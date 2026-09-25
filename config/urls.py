from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shop import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),

    path(
        "add-to-cart/<int:size_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/remove/<int:size_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/increase/<int:size_id>/",
        views.increase_quantity,
        name="increase_quantity"
    ),

    path(
        "cart/decrease/<int:size_id>/",
        views.decrease_quantity,
        name="decrease_quantity"
    ),

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )