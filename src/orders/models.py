from django.db import models
from django.conf import settings
from carts.models import Cart
from decimal import Decimal
from django.db.models.signals import pre_save
# Create your models here.
class UserCheckout(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.CASCADE)
	email = models.EmailField(unique=True)

	def __str__(self):
		return self.email

ADDRESS_TYPE = (
	('billing', 'Billing'),
	('shipping', 'Shipping'),
)

class UserAddress(models.Model):
	user = models.ForeignKey(UserCheckout,on_delete=models.CASCADE)
	type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
	street = models.CharField(max_length=120)
	city = models.CharField(max_length=120)
	state = models.CharField(max_length=120)
	zipcode = models.CharField(max_length=120)

	def get_address(self):
		return "%s, %s, %s %s" %(self.street, self.city, self.state, self.zipcode)
		
	def __str__(self):
		return self.street

class Order(models.Model):
	cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
	user = models.ForeignKey(UserCheckout, null=True,on_delete=models.CASCADE)
	billing_address = models.ForeignKey(UserAddress, related_name='billing_address', null=True,on_delete=models.CASCADE)
	shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', null=True,on_delete=models.CASCADE)
	shipping_total_price = models.DecimalField(max_digits=50, decimal_places=2, default=5.99)
	order_total = models.DecimalField(max_digits=50, decimal_places=2, )

	def __str__(self):
		return str(self.cart.id)

def order_total(sender,instance,*args,**kwargs):
	shipping = instance.shipping_total_price
	total = instance.cart.total
	final = Decimal(shipping) + Decimal(total)
	instance.order_total = final

pre_save.connect(order_total,sender=Order)
