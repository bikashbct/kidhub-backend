from django.contrib import admin
from .models import CategoryConfig, LearnItem


@admin.register(CategoryConfig)
class CategoryConfigAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'slug')
    list_display_links = ('category', 'name')
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(LearnItem)
class LearnItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_label', 'order')
    list_filter = ('category',)
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)
    fields = (
        'name',
        'slug',
        'category',
        'content_name',
        'object_image',
        'object_color',
        'audio',
        'order',
    )

    @admin.display(description='Category')
    def category_label(self, obj):
        return obj.get_category_display()
