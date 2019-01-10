from django.shortcuts import render , get_object_or_404
from django.http import HttpResponseRedirect,Http404,JsonResponse
from django.views.generic.base import View
from .models import Cart,CartItem
from product.models import Variation
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse

class ItemCount(View):
	def get(self,request,*args,**kwargs):
		if request.is_ajax():
			cart_id = self.request.session.get("cart_id")
			if cart_id==None:
				item_count = 0
			else:
				cart = Cart.objects.get(id=cart_id)
				item_count = cart.items.count()
			data = {
				"item_count" : item_count
			}
			request.session['item_count'] = item_count
			return JsonResponse(data)
		else:
			raise Http404



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
			self.request.session["cart_id"] = cart.id
		cart = Cart.objects.get(id=cart_id)
		if self.request.user.is_authenticated:
			cart.user = self.request.user
			cart.save()
		return cart

	def get(self,request,*args,**kwargs):
		cart = self.get_object()
		item_id = request.GET.get("item")
		delete = request.GET.get("delete",False)
		item_added = False
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
			cart_item , created = CartItem.objects.get_or_create(cart=cart,item=item_instance)

			if created:
				item_added = True

			if delete:
				cart_item.delete()
				delete = True
			else:
				cart_item.quantity = qty
				cart_item.save()
			if not request.is_ajax():
				return HttpResponseRedirect(reverse('carts'))

		if request.is_ajax():
			try:
				line_total = cart_item.line_item_total
			except:
				line_total = None
			try:
				total = cart_item.cart.sub_total
			except:
				total = None
			try:
				item_count = cart_item.cart.items.count()
			except:
				item_count = 0

			data = {
				"item_added" : item_added,
				"deleted" : delete,
				"line_total" : line_total,
				"total" : total,
				"item_count" : item_count
			}
			return JsonResponse(data)
		context = {
			"objects" : self.get_object()
		}
		template_name = self.template_name
		return render(request,template_name,context)