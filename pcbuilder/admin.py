from django.contrib import admin
from django.forms import ModelForm
from django import forms
from .models import (
    PCBuild, PCBuildComponent, SavedPCBuild, CompatibilityRule,
    CategoryPC, Computer, PrebuiltPC, PrebuiltPCComponent
)
from store.models import Product, Category

class PrebuiltPCComponentForm(ModelForm):
    class Meta:
        model = PrebuiltPCComponent
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если форма редактируется и есть выбранная категория
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['product'].queryset = Product.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                self.fields['product'].queryset = Product.objects.none()
        elif self.instance.pk and self.instance.category:
            # При редактировании существующего объекта
            self.fields['product'].queryset = Product.objects.filter(category=self.instance.category)
        else:
            # При создании нового объекта
            self.fields['product'].queryset = Product.objects.none()
        
        # Добавляем CSS класс для JavaScript
        self.fields['category'].widget.attrs.update({'class': 'category-select'})
        self.fields['product'].widget.attrs.update({'class': 'product-select'})

class PrebuiltPCComponentInline(admin.TabularInline):
    model = PrebuiltPCComponent
    form = PrebuiltPCComponentForm
    extra = 1
    
    class Media:
        js = ('admin/js/prebuilt_pc_admin.js',)

@admin.register(PrebuiltPC)
class PrebuiltPCAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'level', 'formatted_price', 'created_at')
    list_filter = ('category', 'level', 'created_at')
    search_fields = ('name', 'description')
    inlines = [PrebuiltPCComponentInline]
    
    class Media:
        js = ('admin/js/prebuilt_pc_admin.js',)

@admin.register(PrebuiltPCComponent)
class PrebuiltPCComponentAdmin(admin.ModelAdmin):
    form = PrebuiltPCComponentForm
    list_display = ('prebuilt_pc', 'category', 'product', 'quantity')
    list_filter = ('category', 'prebuilt_pc__category')
    search_fields = ('product__name', 'prebuilt_pc__name')
    
    class Media:
        js = ('admin/js/prebuilt_pc_admin.js',)

@admin.register(CategoryPC)
class CategoryPCAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'description')
    search_fields = ('display_name', 'description')

@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'level', 'formatted_price')
    list_filter = ('category', 'level')
    search_fields = ('name', 'processor', 'graphics_card')

@admin.register(PCBuild)
class PCBuildAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)

@admin.register(SavedPCBuild)
class SavedPCBuildAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'user__username')

@admin.register(CompatibilityRule)
class CompatibilityRuleAdmin(admin.ModelAdmin):
    list_display = ('category1', 'spec1', 'operator', 'category2', 'spec2')
    list_filter = ('category1', 'category2', 'operator')
    search_fields = ('error_message',)
