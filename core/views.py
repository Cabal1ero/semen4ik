from django.shortcuts import render
from .models import HeroSlide, Advantage
from pcbuilder.models import CategoryPC, PrebuiltPC
from django.http import JsonResponse

# Create your views here.
def index(request):
    slides = HeroSlide.objects.filter(active=True)
    advantages = Advantage.objects.filter(active=True)
    return render(request, 'core/index.html', {
        'slides': slides,
        'advantages': advantages,
    })

def about(request):
    return render(request, 'core/about.html')

def support(request):
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
        
        computer_data = {
            'computer': computer,
            'processor': processor.product.name if processor else 'Не указан',
            'graphics_card': graphics_card.product.name if graphics_card else 'Не указана',
            'ram': f"{ram.product.name} x{ram.quantity}" if ram else 'Не указана',
            'storage': storage.product.name if storage else 'Не указан',
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
            
            computer_data = {
                'computer': computer,
                'processor': processor.product.name if processor else 'Не указан',
                'graphics_card': graphics_card.product.name if graphics_card else 'Не указана',
                'ram': f"{ram.product.name} x{ram.quantity}" if ram else 'Не указана',
                'storage': storage.product.name if storage else 'Не указан',
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