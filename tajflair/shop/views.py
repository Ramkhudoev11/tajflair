import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .cart import Cart
from .forms import RegisterForm
from .models import Category, Order, OrderItem, Product, Review

TELEGRAM_BOT_TOKEN = "8928582371:AAEj9JQLtLJlykJSvMMfQreNk7YvEs4bDMs"
TELEGRAM_CHAT_ID = "5317258219"


def send_telegram_message(order, cart):
  message = f"🛍 <b>Новый заказ #{order.id}!</b>\n\n"
  message += f"👤 <b>ФИО:</b> {order.full_name}\n"
  message += f"📞 <b>Телефон:</b> {order.phone}\n"
  message += f"📍 <b>Адрес:</b> {order.address}\n\n"
  message += "📦 <b>Состав заказа:</b>\n"

  for item in cart:
    message += (
        f"• {item['product'].title} x {item['quantity']} —"
        f" {item['total_price']} TJS\n"
    )

  message += f"\n💰 <b>Итого к оплате:</b> {cart.get_total_price()} TJS"

  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
  try:
    requests.post(url, data=payload, timeout=5)
  except Exception as e:
    print(f"Ошибка отправки в Telegram: {e}")


def home(request, category_slug=None):
  category = None
  categories = Category.objects.all()
  products_list = Product.objects.filter(is_available=True).order_by("-id")

  query = request.GET.get("q")
  if query:
    products_list = products_list.filter(title__icontains=query)

  if category_slug:
    category = get_object_or_404(Category, slug=category_slug)
    products_list = products_list.filter(category=category)

  # Пагинация — 8 товаров на страницу
  paginator = Paginator(products_list, 8)
  page_number = request.GET.get("page")
  products = paginator.get_page(page_number)

  return render(
      request,
      "shop/home.html",
      {
          "category": category,
          "categories": categories,
          "products": products,
          "query": query,
      },
  )


def product_detail(request, pk):
  product = get_object_or_404(Product, pk=pk)
  reviews = product.reviews.all()

  if request.method == "POST" and request.user.is_authenticated:
    rating = request.POST.get("rating")
    comment = request.POST.get("comment")

    if rating and comment:
      Review.objects.create(
          product=product, user=request.user, rating=int(rating), comment=comment
      )
      return redirect("product_detail", pk=pk)

  return render(
      request,
      "shop/product_detail.html",
      {
          "product": product,
          "reviews": reviews,
      },
  )


def cart_detail(request):
  cart = Cart(request)
  return render(request, "shop/cart.html", {"cart": cart})


def cart_add(request, product_id):
  cart = Cart(request)
  product = get_object_or_404(Product, id=product_id)
  quantity = int(request.GET.get("quantity", 1))
  cart.add(product=product, quantity=quantity)
  return redirect("cart_detail")


def cart_remove(request, product_id):
  cart = Cart(request)
  product = get_object_or_404(Product, id=product_id)
  cart.remove(product)
  return redirect("cart_detail")


def cart_clear(request):
  cart = Cart(request)
  cart.clear()
  return redirect("cart_detail")


def checkout(request):
  cart = Cart(request)
  if request.method == "POST":
    full_name = request.POST.get("full_name")
    phone = request.POST.get("phone")
    address = request.POST.get("address")

    if full_name and phone and address:
      user = request.user if request.user.is_authenticated else None
      order = Order.objects.create(
          user=user, full_name=full_name, phone=phone, address=address
      )

      for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            price=item["price"],
            quantity=item["quantity"],
        )

      send_telegram_message(order, cart)
      cart.clear()

      return render(
          request,template_name="shop/order_created.html",
          context={"order": order},
      )

  initial_name = ""
  if request.user.is_authenticated:
    initial_name = (
        f"{request.user.first_name} {request.user.last_name}".strip()
        or request.user.username
    )

  return render(
      request,
      template_name="shop/checkout.html",
      context={"cart": cart, "initial_name": initial_name},
  )


def register_view(request):
  if request.method == "POST":
    form = RegisterForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.set_password(form.cleaned_data["password"])
      user.save()
      login(request, user)
      return redirect("home")
  else:
    form = RegisterForm()
  return render(request, "shop/register.html", {"form": form})


def login_view(request):
  if request.method == "POST":
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      return redirect("home")
  else:
    form = AuthenticationForm()
  return render(request, "shop/login.html", {"form": form})


def logout_view(request):
  logout(request)
  return redirect("home")


@login_required(login_url="login")
def profile_view(request):
  orders = Order.objects.filter(user=request.user).order_by("-created_at")
  return render(request, "shop/profile.html", {"orders": orders})