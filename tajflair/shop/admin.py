from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('get_image_preview', 'title', 'price')
    list_display_links = ('get_image_preview', 'title')
    search_fields = ('title',)
    list_filter = ('price',)
    readonly_fields = ('get_image_preview_large',)

    def get_image_preview(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "Нет фото"
    get_image_preview.short_description = "Миниатюра"

    def get_image_preview_large(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "Нет фото"
    get_image_preview_large.short_description = "Предпросмотр фото"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'created_at', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'phone', 'address']
    list_editable = ['status']
    inlines = [OrderItemInline]