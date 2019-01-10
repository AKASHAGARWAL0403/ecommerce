from django.db import models
from product.models import Variation
from django.conf import settings
from decimal import Decimal
from django.db.models.signals import pre_save, post_save, post_delete
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
post_delete.connect(post_sub_total,sender=CartItem)


class Cart(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
	items = models.ManyToManyField(Variation,through=CartItem)
	timestamp = models.DateTimeField(auto_now=False,auto_now_add=True)
	updated = models.DateTimeField(auto_now_add=False,auto_now=True)
	sub_total = models.DecimalField(max_digits=100,decimal_places=2,null=True)
	tax_percentage  = models.DecimalField(max_digits=10, decimal_places=5, default=0.085)
	tax_total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
	total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)

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

def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
	subtotal = Decimal(instance.sub_total)
	tax_total = round(subtotal * Decimal(instance.tax_percentage), 2) #8.5%
	print(instance.tax_percentage)
	total = round(subtotal + Decimal(tax_total), 2)
	instance.tax_total = "%.2f" %(tax_total)
	instance.total = "%.2f" %(total)

pre_save.connect(do_tax_and_total_receiver, sender=Cart)