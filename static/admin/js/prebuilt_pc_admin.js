(function() {
    'use strict';
    
    // Ждем загрузки DOM и jQuery
    function waitForjQuery(callback) {
        if (typeof django !== 'undefined' && django.jQuery) {
            callback(django.jQuery);
        } else if (typeof $ !== 'undefined') {
            callback($);
        } else {
            setTimeout(function() {
                waitForjQuery(callback);
            }, 100);
        }
    }
    
    function updateProductOptions(categorySelect, productSelect, $) {
        const categoryId = categorySelect.val();
        
        if (!categoryId) {
            productSelect.empty().append('<option value="">---------</option>');
            return;
        }
        
        // Показываем индикатор загрузки
        productSelect.empty().append('<option value="">Загрузка...</option>');
        
        // AJAX запрос для получения товаров категории
        $.ajax({
            url: '/pcbuilder/admin/get-products-by-category/',
            data: {
                'category_id': categoryId
            },
            success: function(data) {
                productSelect.empty();
                productSelect.append('<option value="">---------</option>');
                
                $.each(data.products, function(index, product) {
                    productSelect.append(
                        '<option value="' + product.id + '">' + product.name + '</option>'
                    );
                });
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error:', error);
                productSelect.empty().append('<option value="">Ошибка загрузки</option>');
            }
        });
    }
    
    function initializeCategoryProductFilter($) {
        // Функция для привязки событий к элементам
        function bindEvents() {
            // Удаляем старые обработчики чтобы избежать дублирования
            $(document).off('change.categoryFilter', '.category-select');
            
            // Привязываем новый обработчик
            $(document).on('change.categoryFilter', '.category-select', function() {
                const $categorySelect = $(this);
                const $row = $categorySelect.closest('.form-row, tr, .field-category').parent();
                const $productSelect = $row.find('.product-select');
                
                if ($productSelect.length > 0) {
                    updateProductOptions($categorySelect, $productSelect, $);
                }
            });
        }
        
        // Инициализируем события
        bindEvents();
        
        // Обработка добавления новых инлайн форм
        $(document).on('click', '.add-row a, .grp-add-handler', function() {
            setTimeout(function() {
                bindEvents();
            }, 500);
        });
        
        // Для Django Grappelli (если используется)
        $(document).on('formset:added', function() {
            setTimeout(function() {
                bindEvents();
            }, 500);
        });
    }
    
    // Инициализация после загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            waitForjQuery(initializeCategoryProductFilter);
        });
    } else {
        waitForjQuery(initializeCategoryProductFilter);
    }
    
})();
