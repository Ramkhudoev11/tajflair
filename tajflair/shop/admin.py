from django.contrib import admin
from .models import Category, Order, OrderItem, Product, Review


class OrderItemInline(admin.TabularInline):
  model = OrderItem
  raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'full_name', 'phone', 'status', 'created_at']
  list_filter = ['status', 'created_at']
  list_editable = ['status']
  inlines = [OrderItemInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ['name', 'slug']
  prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ['title', 'category', 'price', 'is_available']
  list_filter = ['is_available', 'category']
  list_editable = ['price', 'is_available']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
  list_display = ['product', 'user', 'rating', 'created_at']
  list_filter = ['rating', 'created_at']