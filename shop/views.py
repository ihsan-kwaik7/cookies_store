import os
import logging
import resend

from django.shortcuts import render, redirect
from .models import Cookie, CookieSize, Order, OrderItem

logger = logging.getLogger(__name__)


def home(request):
    cookies = Cookie.objects.filter(available=True)
    return render(request, "home.html", {"cookies": cookies})


def add_to_cart(request, size_id):
    cart = request.session.get("cart", {})
    size_id = str(size_id)

    cart[size_id] = cart.get(size_id, 0) + 1
    request.session["cart"] = cart

    return redirect("home")


def cart(request):
    cart_data = request.session.get("cart", {})
    items = []
    total = 0

    for size_id, quantity in cart_data.items():
        size = CookieSize.objects.get(id=size_id)
        item_total = size.price * quantity
        total += item_total

        items.append({
            "size": size,
            "quantity": quantity,
            "item_total": item_total
        })

    return render(
        request,
        "cart.html",
        {
            "items": items,
            "total": total
        }
    )


def remove_from_cart(request, size_id):
    cart = request.session.get("cart", {})
    size_id = str(size_id)

    if size_id in cart:
        del cart[size_id]

    request.session["cart"] = cart

    return redirect("cart")


def increase_quantity(request, size_id):
    cart = request.session.get("cart", {})
    size_id = str(size_id)

    if size_id in cart:
        cart[size_id] += 1

    request.session["cart"] = cart

    return redirect("cart")


def decrease_quantity(request, size_id):
    cart = request.session.get("cart", {})
    size_id = str(size_id)

    if size_id in cart:
        cart[size_id] -= 1

        if cart[size_id] <= 0:
            del cart[size_id]

    request.session["cart"] = cart

    return redirect("cart")


def checkout(request):
    cart_data = request.session.get("cart", {})

    if not cart_data:
        return redirect("cart")

    items = []
    subtotal = 0

    for size_id, quantity in cart_data.items():
        size = CookieSize.objects.get(id=size_id)

        item_total = size.price * quantity
        subtotal += item_total

        items.append({
            "size": size,
            "quantity": quantity,
            "item_total": item_total
        })

    delivery_fee = 20
    service_fee = 3
    total = subtotal + delivery_fee + service_fee

    if request.method == "POST":

        customer_name = request.POST.get("customer_name")
        phone = request.POST.get("phone")
        city = request.POST.get("city")
        address = request.POST.get("address")

        full_address = f"{city} - {address}"

        order = Order.objects.create(
            customer_name=customer_name,
            phone=phone,
            address=full_address,
            payment_method="cash"
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                cookie=item["size"].cookie,
                size=item["size"],
                quantity=item["quantity"],
                price=item["size"].price
            )

        email_items = ""

        for item in items:
            email_items += (
                f"- {item['size'].cookie.name} | "
                f"{item['size'].name} | "
                f"Quantity: {item['quantity']} | "
                f"{item['item_total']} AED\n"
            )

        email_message = f"""
NEW ORDER - Melted by Jana 🍪

Order Number: #{order.id}

Customer:
Name: {customer_name}
Phone: {phone}

Delivery:
Emirate: {city}
Address: {address}

Order Items:
{email_items}

Subtotal: {subtotal} AED
Delivery Fee: {delivery_fee} AED
Service Fee: {service_fee} AED

TOTAL: {total} AED

Payment Method:
Cash on Delivery

Delivery Time:
Within 2–3 hours, depending on your location.
"""

        api_key = os.getenv("RESEND_API_KEY")

        if not api_key:
            logger.error(
                "RESEND_API_KEY is missing from Render Environment Variables."
            )
        else:
            try:
                resend.api_key = api_key

                response = resend.Emails.send({
                    "from": "onboarding@resend.dev",

                    # ضع هنا إيميلك المسموح من Resend
                    "to": ["ihsanmohamedislam@gmail.com"],

                    "subject": f"New Order #{order.id} - Melted by Jana",

                    "text": email_message,
                })

                logger.info(
                    "RESEND_EMAIL_SUCCESS: %s",
                    response
                )

            except Exception:
                logger.exception(
                    "RESEND_EMAIL_FAILED"
                )

        request.session["cart"] = {}

        return render(
            request,
            "order_success.html",
            {
                "order": order,
                "total": total
            }
        )

    return render(
        request,
        "checkout.html",
        {
            "items": items,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "service_fee": service_fee,
            "total": total,
        }
    )