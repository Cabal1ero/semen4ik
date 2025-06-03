from django.contrib import admin
from .models import HeroSlide, Advantage

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'active')
    list_editable = ('order', 'active')
    search_fields = ('title',)
    ordering = ('order',)

@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'active')
    list_editable = ('icon', 'order', 'active')
    search_fields = ('title',)
    ordering = ('order',)
