from django.db import models
from product.models import Variation
from django.conf import settings
from decimal import Decimal
from django.db.models.signals import pre_save, post_save
# Create your models here.

class CartItem(models.Model):
	cart = models.ForeignKey("Cart",on_delete=models.CASCADE)
	item = models.ForeignKey(Variation,on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	line_item_total = models.DecimalField(max_digits=100,decimal_places=2)
	def __str__(self):
		return self.item.title

	def remove(self):
		return self.item.remove_from_cart()

def pre_add_line_total(sender,instance,*args,**kwrags):
	qty = int(instance.quantity)
	if qty >= 1:
		price = instance.item.get_price()
		instance.line_item_total = Decimal(qty) * Decimal(price)

pre_save.connect(pre_add_line_total,sender=CartItem)


def post_sub_total(sender,instance,*args,**kwrags):
	instance.cart.get_total()

post_save.connect(post_sub_total,sender=CartItem)

class Cart(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	items = models.ManyToManyField(Variation,through=CartItem)
	timestamp = models.DateTimeField(auto_now=False,auto_now_add=True)
	upadted = models.DateTimeField(auto_now_add=False,auto_now=True)
	sub_total = models.DecimalField(max_digits=100,decimal_places=2)

	def __str__(self):
		return str(self.id)

	def get_total(self):
		print("gdfsdfss")
		subtotal = 0
		items = self.cartitem_set.all()
		for item in items:
			subtotal += item.line_item_total
		self.sub_total = subtotal
		print(subtotal)
		self.save()