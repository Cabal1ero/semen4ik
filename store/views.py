from django.shortcuts import render, get_object_or_404
from .models import ProductLine, Category, Product
# Create your views here.
def index(request):
    return render(request, 'store/index.html')

def catalog(request):
    product_lines = ProductLine.objects.all()
    return render(request, 'store/catalog.html', {'product_lines': product_lines})

def category_detail(request, product_line_slug, category_slug):
    product_line = get_object_or_404(ProductLine, slug=product_line_slug)
    category = get_object_or_404(Category, slug=category_slug, product_line=product_line)
    products = category.products.all()
    cart_product_ids = []
    wishlist_product_ids = []
    if request.user.is_authenticated:
        cart_product_ids = list(request.user.cart_items.values_list('product_id', flat=True))
        wishlist_product_ids = list(request.user.favorite_items.values_list('product_id', flat=True))
    return render(request, 'store/category_detail.html', {
        'product_line': product_line,
        'category': category,
        'products': products,
        'cart_product_ids': cart_product_ids,
        'wishlist_product_ids': wishlist_product_ids,
    })


def product_detail(request, product_line_slug, category_slug, product_slug):
    product_line = get_object_or_404(ProductLine, slug=product_line_slug)
    category = get_object_or_404(Category, slug=category_slug, product_line=product_line)
    product = get_object_or_404(Product, slug=product_slug, category=category)
    images = product.images.all()
    specs = product.specs.select_related('specification').all()
    cart_product_ids = []
    wishlist_product_ids = []
    if request.user.is_authenticated:
        cart_product_ids = list(request.user.cart_items.values_list('product_id', flat=True))
        wishlist_product_ids = list(request.user.favorite_items.values_list('product_id', flat=True))
    return render(request, 'store/product_detail.html', {
        'product': product,
        'images': images,
        'specs': specs,
        'category': category,
        'product_line': product_line,
        'cart_product_ids': cart_product_ids,
        'wishlist_product_ids': wishlist_product_ids,
    })

