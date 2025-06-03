from django.db import models
from django.conf import settings
from store.models import Product

# Create your models here.

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
