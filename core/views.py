from django.shortcuts import render, redirect
from .models import HeroSlide, Advantage, SupportTicket
from pcbuilder.models import CategoryPC, PrebuiltPC
from django.http import JsonResponse
from store.models import Product, Category, ProductLine
from django.db.models import Count
from django.contrib import messages

# Create your views here.
def index(request):
    slides = HeroSlide.objects.filter(is_active=True).order_by('order')
    advantages = Advantage.objects.all().order_by('order')
    
    # Получаем 4 случайных товара
    random_products = Product.objects.order_by('?')[:4]
    
    # Получаем популярные категории (например, по количеству товаров)
    popular_categories = Category.objects.annotate(
        num_products=Count('products')
    ).order_by('-num_products')[:4]
    
    # Получаем разделы для каталога
    product_lines = ProductLine.objects.all()

    context = {
        'slides': slides,
        'advantages': advantages,
        'random_products': random_products,
        'popular_categories': popular_categories,
        'product_lines': product_lines,
    }
    return render(request, 'core/index.html', context)

def about(request):
    return render(request, 'core/about.html')

def support_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            topic = request.POST.get('topic')
            message_text = request.POST.get('message')

            if not all([name, email, topic, message_text]):
                messages.error(request, 'Пожалуйста, заполните все поля.')
                return redirect('core:support')

            ticket = SupportTicket.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                topic=topic,
                message=message_text
            )
            messages.success(request, 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
            return redirect('core:support')
        
        except Exception as e:
            messages.error(request, f'Произошла ошибка: {e}')
            return redirect('core:support')

    return render(request, 'core/support.html')

def payments(request):
    return render(request, 'core/payments.html')

def delivery(request):
    return render(request, 'core/delivery.html')
from store.models import Product
from pcbuilder.models import CategoryPC, Computer, PrebuiltPC

def computer_catalog(request):
    """Каталог готовых компьютеров"""
    categories = CategoryPC.objects.all()
    computers = PrebuiltPC.objects.prefetch_related('components__product', 'components__category')
    
    # Фильтрация по категории
    category_filter = request.GET.get('category')
    if category_filter:
        computers = computers.filter(category__name=category_filter)
    
    # Фильтрация по уровню
    level_filter = request.GET.get('level')
    if level_filter:
        computers = computers.filter(level=level_filter)
    
    # Добавляем информацию о компонентах для каждого компьютера
    computers_with_details = []
    for computer in computers:
        components = computer.components.all()
        
        # Извлекаем основные компоненты
        processor = components.filter(category__slug='processor').first()
        graphics_card = components.filter(category__slug='videokarta').first()
        ram = components.filter(category__slug='ram').first()
        storage = components.filter(category__slug='storage').first()
        motherboard = components.filter(category__slug='motherboard').first()
        power_supply = components.filter(category__slug='psu').first()
        case = components.filter(category__slug='case').first()
        
        computer_data = {
            'computer': computer,
            'processor': processor.product.name if processor else '',
            'graphics_card': graphics_card.product.name if graphics_card else '',
            'ram': f"{ram.product.name} x{ram.quantity}" if ram else '',
            'storage': storage.product.name if storage else '',
            'motherboard': motherboard.product.name if motherboard else '',
            'power_supply': power_supply.product.name if power_supply else '',
            'case': case.product.name if case else '',
            'components': components,
        }
        computers_with_details.append(computer_data)
    
    context = {
        'categories': categories,
        'computers': computers_with_details,
        'selected_category': category_filter,
        'selected_level': level_filter,
    }
    
    return render(request, 'core/pc.html', context)

from django.template.loader import render_to_string
from django.http import JsonResponse

def get_computers_by_category(request, category_name):
    """AJAX endpoint для получения компьютеров по категории"""
    try:
        category = CategoryPC.objects.get(name=category_name)
        computers = PrebuiltPC.objects.filter(category=category).prefetch_related('components__product', 'components__category')
        
        # Подготавливаем данные о компьютерах с компонентами
        computers_with_details = []
        for computer in computers:
            components = computer.components.all()
            
            # Извлекаем основные компоненты
            processor = components.filter(category__slug='processor').first()
            graphics_card = components.filter(category__slug='videokarta').first()
            ram = components.filter(category__slug='ram').first()
            storage = components.filter(category__slug='storage').first()
            motherboard = components.filter(category__slug='motherboard').first()
            power_supply = components.filter(category__slug='psu').first()
            case = components.filter(category__slug='case').first()
            
            computer_data = {
                        'computer': computer,
                        'processor': processor.product.name if processor else '',
                        'graphics_card': graphics_card.product.name if graphics_card else '',
                        'ram': f"{ram.product.name} x{ram.quantity}" if ram else '',
                        'storage': storage.product.name if storage else '',
                        'motherboard': motherboard.product.name if motherboard else '',
                        'power_supply': power_supply.product.name if power_supply else '',
                        'case': case.product.name if case else '',
                        'components': components,
                    }
            computers_with_details.append(computer_data)
        
        # Рендерим только секцию с компьютерами
        html = render_to_string('core/pc_section.html', {
            'computers': computers_with_details
        })
        
        return JsonResponse({
            'success': True,
            'html': html
        })
    except CategoryPC.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Категория не найдена'
        })
