from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render , get_object_or_404 , redirect
from django.http import HttpResponseRedirect,Http404,JsonResponse
from django.views.generic.base import View
from .models import Cart,CartItem
from product.models import Variation
from django.views.generic.detail import SingleObjectMixin , DetailView
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
			try:
				tax_amount = cart_item.cart.tax_total
			except:
				tax_amount = 0
			try:
				total_amount = cart_item.cart.total
			except:
				total_amount = 0
			data = {
				"item_added" : item_added,
				"deleted" : delete,
				"line_total" : line_total,
				"total" : total,
				"item_count" : item_count,
				"tax_amount" : tax_amount,
				"total_amount" : total_amount
			}
			return JsonResponse(data)
		context = {
			"objects" : self.get_object()
		}
		template_name = self.template_name
		return render(request,template_name,context)

class CheckOutView(DetailView):
	model = Cart
	template_name = 'carts/checkout.html'

	def get_object(self,*args,**kwargs):
		cart_id = self.request.session.get("cart_id")
		if cart_id==None:
			return redirect('carts')
		else:
			cart = Cart.objects.get(id=cart_id)
		return cart

	def get_context_data(self,*args,**kwargs):
		context = super(CheckOutView,self).get_context_data(*args,**kwargs)
		user_can_continue = False
		print("AAKAKKAKAKAKAKKAAK")
		print(self.request.user.is_authenticated)
		if not self.request.user.is_authenticated:
			context['login_form'] = AuthenticationForm()
			context['next_url'] = self.request.build_absolute_uri()
		if self.request.user.is_authenticated:
			user_can_continue = True
		print("user_can_continue",user_can_continue)
		context['user_can_continue'] = user_can_continue
		return context
		
