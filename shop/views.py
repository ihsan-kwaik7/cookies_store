from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .models import Cookie, CookieSize, Order, OrderItem


def home(request):
    cookies = Cookie.objects.filter(available=True)

    return render(
        request,
        "home.html",
        {
            "cookies": cookies,
        }
    )


def add_to_cart(request, size_id):
    cart = request.session.get("cart", {})

    size_id = str(size_id)

    if size_id in cart:
        cart[size_id] += 1
    else:
        cart[size_id] = 1

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
            "item_total": item_total,
        })

    return render(
        request,
        "cart.html",
        {
            "items": items,
            "total": total,
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
            "item_total": item_total,
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

        send_mail(
            subject=f"New Order #{order.id} - Melted by Jana",
            message=email_message,
            from_email=None,
            recipient_list=["kwaikjana@gmail.com"],
            fail_silently=False,
        )

        request.session["cart"] = {}

        return render(
            request,
            "order_success.html",
            {
                "order": order,
                "total": total,
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