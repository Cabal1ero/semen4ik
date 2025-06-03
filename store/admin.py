from django.contrib import admin
from .models import ProductLine, Category, Specification, Product, ProductImage, ProductSpec
from django.utils.html import format_html

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'order', 'is_main', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px; max-width: 120px;" />', obj.image.url)
        return ""
    image_preview.short_description = 'Превью'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount', 'final_price_display', 'meta_title', 'image_preview')
    list_filter = ('category', 'discount')
    search_fields = ('name', 'description', 'meta_title', 'meta_description')
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'price', 'discount', 'image', 'image_preview')
        }),
        ('Описание и SEO', {
            'fields': ('description', 'meta_title', 'meta_description')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return ""
    image_preview.short_description = 'Главное фото'

    def final_price_display(self, obj):
        return f"{obj.final_price:.2f} ₽"
    final_price_display.short_description = 'Цена со скидкой'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'is_main', 'alt_text', 'image_preview')
    list_filter = ('is_main', 'product')
    search_fields = ('alt_text',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 90px;" />', obj.image.url)
        return ""
    image_preview.short_description = 'Превью'

@admin.register(ProductLine)
class ProductLineAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_line', 'slug')
    list_filter = ('product_line',)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(ProductSpec)
class ProductSpecAdmin(admin.ModelAdmin):
    list_display = ('product', 'specification', 'value')
    list_filter = ('specification', 'product')
    search_fields = ('value',)
