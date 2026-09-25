from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from .cart import Cart


def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    return render(request, 'shop/home.html', {  # <-- Добавили shop/
        'categories': categories,
        'products': products
    })


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'shop/home.html', {  # <-- Добавили shop/
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})  # <-- Добавили shop/


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})  # <-- Добавили shop/


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart_detail')


def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        cart.clear()
        return render(request, 'shop/checkout.html', {'success': True})  # <-- Добавили shop/
    return render(request, 'shop/checkout.html', {'cart': cart})  # <-- Добавили shop/