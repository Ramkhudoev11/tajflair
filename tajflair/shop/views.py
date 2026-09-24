import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Order, OrderItem
from .cart import Cart

# Настройки Telegram бота (вставь сюда НОВЫЙ токен от @BotFather!)
TELEGRAM_BOT_TOKEN = '8928582371:AAEj9JQLtLJlykJSvMMfQreNk7YvEs4bDMs'
TELEGRAM_CHAT_ID = '5317258219'


def send_telegram_notification(order):
    """Отправка уведомления о новом заказе в Telegram"""
    items_text = ""
    for item in order.items.all():
        items_text += f"— {item.product.title} (x{item.quantity}) — {item.price * item.quantity} TJS\n"

    message = (
        f"🛍 <b>НОВЫЙ ЗАКАЗ №{order.id}</b>\n\n"
        f"<b>Клиент:</b> {order.full_name}\n"
        f"<b>Телефон:</b> {order.phone}\n"
        f"<b>Адрес:</b> {order.address}\n\n"
        f"<b>Состав заказа:</b>\n{items_text}"
    )

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


def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    return render(request, 'shop/home.html', {'categories': categories, 'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    return render(request, 'shop/product_detail.html', {'product': product})


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product_id=product.id)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})


def order_create(request):
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
            send_telegram_notification(order)

            cart.clear()
            return render(request, 'shop/order_created.html', {'order': order})

    return render(request, 'shop/checkout.html', {'cart': cart})