from .models import Order
from carts.models import Cart
from django.shortcuts import render , get_object_or_404 , redirect
from django.http import HttpResponseRedirect

class CheckoutMixin():
	def get_order(self,*args,**kwargs):
		cart = self.get_cart()
		new_order_id = self.request.session.get("order_id")
		#print('akash' , new_order_id)
		if new_order_id != None:
			new_order = Order.objects.get(id = new_order_id)
		else:
			new_order = Order.objects.create(cart = cart)
			self.request.session['order_id'] = new_order.id
	#	new_order.cart = cart
		return new_order

	def get_cart(self,*args,**kwargs):
		cart_id = self.request.session.get("cart_id")
		if cart_id==None:
			return None
		else:
			cart = Cart.objects.get(id=cart_id)
		if cart.items.count() == 0:
			return None
		return cart