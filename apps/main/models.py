from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    color = models.CharField(max_length=55)
    size = models.CharField(max_length=55)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='products', default='', blank=True)
    image_url = models.CharField(max_length=5000, default='', blank=True)
    image_url2 = models.CharField(max_length=5000, default='', blank=True)
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(x.value for x in ratings) // ratings.count()
        return 0
    
    def __str__(self) -> str:
        return self.title
    

class Order(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='orders'
	)
	is_paid = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	@property
	def total_price(self):
		items = self.items.all()
		if items.exists():
			return sum(item.product.price * item.quantity for item in items)
		return 0


class OrderItem(models.Model):
	order = models.ForeignKey(
		Order,
		on_delete=models.CASCADE,
		related_name='items'
	)
	product = models.ForeignKey(
		Product,
		on_delete=models.RESTRICT
	)
	quantity = models.PositiveIntegerField(default=1)


class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.user} -> {self.product}'


class Rating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    value = models.IntegerField(
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    )

    def __str__(self) -> str:
        return f'{self.user} -> {self.product}'

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    def __str__(self) -> str:
        return f'{self.user} -> {self.product}'