from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from decimal import Decimal

# Create your models here.

class ProductLine(models.Model):
    """Разделы товаров (Комплектующие, Периферия)"""
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Category(models.Model):
    """Категории (Процессоры, Видеокарты)"""
    product_line = models.ForeignKey(
        ProductLine,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True)

    PROTECTED_SLUGS = [
        'videokarta', 'processor', 'motherboard', 'storage',
        'case', 'ram', 'cooling', 'psu'
    ]

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        unique_together = ('product_line', 'name')

    def __str__(self):
        return f"{self.product_line.name} → {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.pk:
            orig = Category.objects.get(pk=self.pk)
            if orig.slug in self.PROTECTED_SLUGS:
                raise Exception("Изменение этой категории запрещено!")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.slug in self.PROTECTED_SLUGS:
            raise Exception("Удаление этой категории запрещено!")
        super().delete(*args, **kwargs)

class Specification(models.Model):
    """Характеристики категории"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='specifications'
    )
    name = models.CharField('Название', max_length=100)
    unit = models.CharField('Единица измерения', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Product(models.Model):
    """Товары"""
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True)
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    discount = models.PositiveIntegerField('Скидка (%)', default=0)
    description = models.TextField(
        'Описание',
        blank=True,
        default='',
        help_text='Можно использовать HTML-теги для форматирования текста (например, <ul>, <li>, <b>, <h3> и т.д.)'
    )
    meta_title = models.CharField('SEO Title', max_length=255, blank=True, default='', help_text='Заголовок для SEO (meta title)')
    meta_description = models.CharField('SEO Description', max_length=500, blank=True, default='', help_text='Описание для SEO (meta description)')
    image = models.ImageField('Фото', upload_to='products/', blank=True, null=True)
    # Галерея изображений будет через отдельную модель ProductImage

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        if self.discount:
            # Преобразуем discount в Decimal для корректного вычисления
            discount_decimal = Decimal(str(self.discount)) / Decimal('100')
            return self.price * (Decimal('1') - discount_decimal)
        return self.price

    def formatted_price(self):
        """Форматированная цена с разделителями"""
        return f"{int(self.final_price):,}".replace(',', ' ') + ' ₽'

class ProductImage(models.Model):
    """Галерея изображений для товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Изображение', upload_to='products/gallery/')
    alt_text = models.CharField('Описание изображения', max_length=255, blank=True, default='')
    order = models.PositiveIntegerField('Порядок', default=0, help_text='Для сортировки изображений')
    is_main = models.BooleanField('Основное изображение', default=False, help_text='Показывать как главное')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Галерея изображений'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} — {self.alt_text or self.image.name}"

class ProductSpec(models.Model):
    """Значения характеристик для товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs')
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE)
    value = models.CharField('Значение', max_length=100)

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'
        unique_together = ('product', 'specification')

    def __str__(self):
        return f"{self.product.name}: {self.specification.name} = {self.value}"
