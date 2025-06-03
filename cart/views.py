from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import CartItem
from store.models import Product
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    order_sum = sum(item.product.price * item.quantity for item in cart_items)
    total_sum = sum(item.product.final_price * item.quantity for item in cart_items)
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'order_sum': order_sum,
        'total_sum': total_sum,
    })

@require_POST
@csrf_exempt
@login_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден.'}, status=404)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    max_qty = getattr(product, 'stock', 99)
    if not created:
        if cart_item.quantity + quantity > max_qty:
            cart_item.quantity = max_qty
        else:
            cart_item.quantity += quantity
        cart_item.save()
    else:
        cart_item.quantity = min(quantity, max_qty)
        cart_item.save()
    return JsonResponse({'success': True, 'quantity': cart_item.quantity, 'max_qty': max_qty})

@require_POST
@csrf_exempt
@login_required
def remove_from_cart(request):
    product_id = request.POST.get('product_id')
    try:
        cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return JsonResponse({'success': True, 'quantity': cart_item.quantity})
        else:
            cart_item.delete()
            return JsonResponse({'success': True, 'removed': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден в корзине.'}, status=404)

@require_POST
@csrf_exempt
@login_required
def add_to_cart_by_slug(request, product_slug):
    try:
        product = Product.objects.get(slug=product_slug)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден.'}, status=404)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()
    return JsonResponse({'success': True, 'in_cart': True, 'quantity': cart_item.quantity})

@require_POST
@csrf_exempt
@login_required
def remove_from_cart_by_slug(request, product_slug):
    try:
        cart_item = CartItem.objects.get(user=request.user, product__slug=product_slug)
        cart_item.delete()
        return JsonResponse({'success': True, 'in_cart': False})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден в корзине.'}, status=404)
