from django.contrib import admin
from .models import Category, LearnItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(LearnItem)
class LearnItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
