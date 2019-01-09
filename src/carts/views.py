from django.shortcuts import render , get_object_or_404
from django.http import HttpResponseRedirect,Http404
from django.views.generic.base import View
from .models import Cart,CartItem
from product.models import Variation
from django.views.generic.detail import SingleObjectMixin


class CartView(SingleObjectMixin,View):
	model = Cart
	template_name = 'carts/view.html'

	def get_object(self,*args,**kwargs):
		self.request.session.set_expiry(0)
		cart_id = self.request.session.get("cart_id")
		print(cart_id == None)
		print(cart_id)
		if cart_id==None:
			cart = Cart()
			cart.save()
			cart_id = cart.id
			print("gbdfvdc")
			self.request.session["cart_id"] = cart.id
		cart = Cart.objects.get(id=cart_id)
		if self.request.user.is_authenticated:
			cart.user = self.request.user
			cart.save()
		return cart

	def get(self,request,*args,**kwargs):
		cart = self.get_object()
		item_id = request.GET.get("item")
		delete = request.GET.get("delete")
		if item_id:
			item_instance = get_object_or_404(Variation,id=item_id)
			print(item_instance)
			qty = request.GET.get("qty",1)

		try:
			if int(qty) < 1:
				delete = True
		except:
			raise Http404
		print(cart , item_instance)
		cart_item = CartItem.objects.get_or_create(cart=cart,item=item_instance)[0]
		if delete:
			cart_item.delete()
		else:
			cart_item.quantity = qty
			cart_item.save()

		context = {
			"objects" : self.get_object()
		}
		template_name = self.template_name
		return render(request,template_name,context)