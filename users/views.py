from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .forms import  UserUpdateForm as CustomUserCreationForm, UserRegisterForm as CustomAuthenticationForm
from store.models import PromoCode, PromoCodeUsage, UserPromoCode
from pcbuilder.models import SavedPCBuild
from order.models import Order

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('index')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы.')
    return redirect('index')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

@require_GET
@login_required
def get_user_promocodes(request):
    """API для получения промокодов пользователя"""
    try:
        # Получаем персональные промокоды
        personal_promocodes = UserPromoCode.objects.filter(
            user=request.user
        ).select_related('promocode')
        
        # Получаем использованные промокоды
        used_promocodes = PromoCodeUsage.objects.filter(
            user=request.user
        ).select_related('promocode').order_by('-used_at')
        
        # Получаем доступные промокоды (общие)
        available_promocodes = PromoCode.objects.filter(
            status='active'
        ).exclude(
            # Исключаем уже использованные
            id__in=used_promocodes.values_list('promocode_id', flat=True)
        )
        
        # Формируем ответ
        promocodes_data = {
            'personal': [],
            'available': [],
            'used': []
        }
        
        # Персональные промокоды
        for user_promo in personal_promocodes:
            promo = user_promo.promocode
            is_valid, error_msg = promo.is_valid(user=request.user)
            
            promocodes_data['personal'].append({
                'id': promo.id,
                'code': promo.code,
                'name': promo.name,
                'description': promo.description,
                'discount_type': promo.discount_type,
                'discount_value': float(promo.discount_value),
                'min_order_amount': float(promo.min_order_amount),
                'end_date': promo.end_date.strftime('%d.%m.%Y'),
                'is_valid': is_valid,
                'error_message': error_msg if not is_valid else None,
                'assigned_at': user_promo.assigned_at.strftime('%d.%m.%Y %H:%M')
            })
        
        # Доступные промокоды
        for promo in available_promocodes[:5]:  # Показываем только первые 5
            is_valid, error_msg = promo.is_valid(user=request.user)
            
            promocodes_data['available'].append({
                'id': promo.id,
                'code': promo.code,
                'name': promo.name,
                'description': promo.description,
                'discount_type': promo.discount_type,
                'discount_value': float(promo.discount_value),
                'min_order_amount': float(promo.min_order_amount),
                'end_date': promo.end_date.strftime('%d.%m.%Y'),
                'is_valid': is_valid,
                'error_message': error_msg if not is_valid else None
            })
        
        # Использованные промокоды
        for usage in used_promocodes[:10]:  # Показываем последние 10
            promocodes_data['used'].append({
                'id': usage.promocode.id,
                'code': usage.promocode.code,
                'name': usage.promocode.name,
                'discount_amount': float(usage.discount_amount),
                'order_amount': float(usage.order_amount),
                'used_at': usage.used_at.strftime('%d.%m.%Y %H:%M'),
                'order_id': usage.order_id
            })
        
        return JsonResponse({
            'success': True,
            'promocodes': promocodes_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'promocodes': []
        })

@require_GET
@login_required
def get_user_configurations(request):
    """API для получения конфигураций пользователя"""
    try:
        configurations = SavedPCBuild.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        configs_data = []
        for config in configurations:
            # Подсчитываем общую стоимость
            total_price = sum(
                item.get('price', 0) * item.get('quantity', 1) 
                for item in config.data
            )
            
            # Получаем основные компоненты
            components_summary = []
            for item in config.data[:4]:  # Показываем первые 4 компонента
                components_summary.append({
                    'category_name': item.get('category_name', ''),
                    'product_name': item.get('product_name', ''),
                    'price': item.get('price', 0),
                    'quantity': item.get('quantity', 1)
                })
            
            configs_data.append({
                'id': config.id,
                'name': config.name,
                'created_at': config.created_at.strftime('%d.%m.%Y %H:%M'),
                'total_price': total_price,
                'components_count': len(config.data),
                'components_summary': components_summary
            })
        
        return JsonResponse({
            'success': True,
            'configurations': configs_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_GET
@login_required
def get_user_orders(request):
    """API для получения заказов пользователя"""
    try:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
        
        orders_data = []
        for order in orders:
            # Получаем товары заказа
            order_items = []
            for item in order.items.all():
                order_items.append({
                    'product_name': item.product_name,
                    'product_price': float(item.product_price),
                    'quantity': item.quantity,
                    'total_price': float(item.product_price * item.quantity)
                })
            
            # Определяем статус на русском
            status_display = {
                'pending': 'Ожидает обработки',
                'confirmed': 'Подтвержден',
                'processing': 'В обработке',
                'shipped': 'Отправлен',
                'delivered': 'Доставлен',
                'cancelled': 'Отменен'
            }.get(order.status, order.status)
            
            # Определяем цвет статуса
            status_color = {
                'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
                'confirmed': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
                'processing': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
                'shipped': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
                'delivered': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
                'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
            }.get(order.status, 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300')
            
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'status': order.status,
                'status_display': status_display,
                'status_color': status_color,
                'total_amount': float(order.total_amount),
                'discount_amount': float(order.discount_amount),
                'subtotal': float(order.subtotal),
                'promocode_used': order.promocode_used,
                'payment_method': order.get_payment_method_display(),
                'items_count': order.items.count(),
                'items': order_items,
                'delivery_address': f"{order.delivery_city}, {order.delivery_street}, {order.delivery_house}" + 
                                  (f", кв. {order.delivery_apartment}" if order.delivery_apartment else "")
            })
        
        return JsonResponse({
            'success': True,
            'orders': orders_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })