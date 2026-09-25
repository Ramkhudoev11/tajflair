from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
  name = models.CharField(max_length=200, verbose_name="Название")
  slug = models.SlugField(unique=True, verbose_name="Slug")

  class Meta:
    verbose_name = "Категория"
    verbose_name_plural = "Категории"

  def __str__(self):
    return self.name


class Product(models.Model):
  category = models.ForeignKey(
      Category,
      related_name="products",
      on_delete=models.CASCADE,
      null=True,
      blank=True,
      verbose_name="Категория",
  )
  title = models.CharField(max_length=255, verbose_name="Название")
  description = models.TextField(blank=True, verbose_name="Описание")
  price = models.DecimalField(
      max_digits=10, decimal_places=2, verbose_name="Цена"
  )
  image = models.ImageField(
      upload_to="products/", blank=True, null=True, verbose_name="Изображение"
  )
  is_available = models.BooleanField(default=True, verbose_name="В наличии")

  class Meta:
    verbose_name = "Товар"
    verbose_name_plural = "Товары"

  def __str__(self):
    return self.title

  def get_image_url(self):
    if hasattr(self, "image") and self.image:
      return self.image.url
    if hasattr(self, "photo") and self.photo:
      return self.photo.url
    if hasattr(self, "img") and self.img:
      return self.img.url
    return ""

  def get_average_rating(self):
    reviews = self.reviews.all()
    if reviews.exists():
      return round(sum(r.rating for r in reviews) / reviews.count(), 1)
    return 0


class Review(models.Model):
  product = models.ForeignKey(
      Product,
      on_delete=models.CASCADE,
      related_name="reviews",
      verbose_name="Товар",
  )
  user = models.ForeignKey(
      User, on_delete=models.CASCADE, verbose_name="Пользователь"
  )
  rating = models.PositiveSmallIntegerField(
      validators=[MinValueValidator(1), MaxValueValidator(5)],
      verbose_name="Оценка (1-5)",
  )
  comment = models.TextField(verbose_name="Отзыв")
  created_at = models.DateTimeField(
      auto_now_add=True, verbose_name="Дата создания"
  )

  class Meta:
    verbose_name = "Отзыв"
    verbose_name_plural = "Отзывы"
    ordering = ["-created_at"]

  def __str__(self):
    return f"{self.user.username} - {self.product.title} ({self.rating}★)"


class Order(models.Model):
  STATUS_CHOICES = (
      ("new", "Новый"),
      ("in_progress", "В обработке"),
      ("completed", "Завершен"),
      ("canceled", "Отменен"),
  )

  user = models.ForeignKey(
      User,
      on_delete=models.CASCADE,
      related_name="orders",
      null=True,
      blank=True,
      verbose_name="Пользователь",
  )
  full_name = models.CharField(max_length=255, verbose_name="Имя клиента")
  phone = models.CharField(max_length=20, verbose_name="Телефон")
  address = models.TextField(verbose_name="Адрес доставки")
  status = models.CharField(
      max_length=20,
      choices=STATUS_CHOICES,
      default="new",
      verbose_name="Статус",
  )
  created_at = models.DateTimeField(
      auto_now_add=True, verbose_name="Дата заказа"
  )

  class Meta:
    verbose_name = "Заказ"
    verbose_name_plural = "Заказы"

  def __str__(self):
    return f"Заказ #{self.id} — {self.full_name}"

  def get_total_cost(self):
    return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
  order = models.ForeignKey(
      Order,
      related_name="items",
      on_delete=models.CASCADE,
      verbose_name="Заказ",
  )
  product = models.ForeignKey(
      Product, on_delete=models.CASCADE, verbose_name="Товар"
  )
  price = models.DecimalField(
      max_digits=10, decimal_places=2, verbose_name="Цена"
  )
  quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

  class Meta:
    verbose_name = "Элемент заказа"
    verbose_name_plural = "Элементы заказа"

  def __str__(self):
    return f"{self.product.title} x {self.quantity}"

  def get_cost(self):
    return self.price * self.quantity