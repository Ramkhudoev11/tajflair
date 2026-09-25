from decimal import Decimal
from django.conf import settings
from .models import Product


class Cart:
    def __init__(self, request):
        """
        Инициализация корзины.
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Добавление товара в корзину или обновление его количества.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        if self.cart[product_id]['quantity'] <= 0:
            self.remove(product)
        else:
            self.save()

    def remove(self, product):
        """
        Удаление товара из корзины.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """
        Очистка корзины из сессии.
        """
        if 'cart' in self.session:
            del self.session['cart']
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        """
        Перебор элементов в корзине с подтяжкой объектов Product из БД.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        products_map = {str(product.id): product for product in products}

        cart = self.cart.copy()

        for product_id, item in cart.items():
            product = products_map.get(str(product_id))
            item['product'] = product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )