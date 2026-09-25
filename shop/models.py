from django.db import models


class Cookie(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="cookies/", blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CookieSize(models.Model):
    cookie = models.ForeignKey(
        Cookie,
        on_delete=models.CASCADE,
        related_name="sizes"
    )
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.cookie.name} - {self.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("cash", "Cash on Delivery"),
    ]

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    address = models.TextField()

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="cash"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    cookie = models.ForeignKey(
        Cookie,
        on_delete=models.CASCADE
    )
    size = models.ForeignKey(
        CookieSize,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.cookie.name} - {self.size.name}"