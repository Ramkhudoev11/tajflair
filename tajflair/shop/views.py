import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, OrderItem
from .cart import Cart

# Настройки Telegram-бота
TELEGRAM_BOT_TOKEN = '8928582371:AAEj9JQLtLJlykJSvMMfQreNk7YvEs4bDMs'
TELEGRAM_CHAT_ID = '5317258219'

def send_telegram_message(order, cart):
    message = f"🛍 <b>Новый заказ #{order.id}!</b>\n\n"
    message += f"👤 <b>ФИО:</b> {order.full_name}\n"
    message += f"📞 <b>Телефон:</b> {order.phone}\n"
    message += f"📍 <b>Адрес:</b> {order.address}\n\n"
    message += "📦 <b>Состав заказа:</b>\n"

    for item in cart:
        message += f"• {item['product'].title} x {item['quantity']} — {item['total_price']} TJS\n"

    message += f"\n💰 <b>Итого к оплате:</b> {cart.get_total_price()} TJS"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")


def home(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'shop/home.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})


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
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if full_name and phone and address:
            order = Order.objects.create(
                full_name=full_name,
                phone=phone,
                address=address
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            # Отправка уведомления в Telegram
            send_telegram_message(order, cart)

            # Очищаем корзину
            cart.clear()

            return render(request, 'shop/order_created.html', {'order': order})

    return render(request, 'shop/checkout.html', {'cart': cart})