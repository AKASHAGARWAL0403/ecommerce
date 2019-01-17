from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render , get_object_or_404 , redirect
from django.http import HttpResponseRedirect,Http404,JsonResponse
from django.views.generic.base import View
from .models import Cart,CartItem
from product.models import Variation
from django.views.generic.detail import SingleObjectMixin , DetailView
from django.urls import reverse
from django.views.generic.edit import FormMixin
from orders.forms import GuestCheckoutForm
from orders.models import UserCheckout , UserAddress
from orders.models import Order

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

class CheckOutView(FormMixin,DetailView):
	model = Cart
	template_name = 'carts/checkout.html'
	form_class = GuestCheckoutForm

	def get_object(self,*args,**kwargs):
		cart_id = self.request.session.get("cart_id")
	#	print("akash is ")
	#	print(cart_id)
		if cart_id==None:
			return redirect('carts')
		else:
			cart = Cart.objects.get(id=cart_id)
		return cart

	def get_context_data(self,*args,**kwargs):
		form = self.get_form()
		user_checkout_id = self.request.session.get("user_checkout_id")
		context = super(CheckOutView,self).get_context_data(*args,**kwargs)
		user_can_continue = False
		if not self.request.user.is_authenticated or user_checkout_id == None:
			context['login_form'] = AuthenticationForm()
			context['next_url'] = self.request.build_absolute_uri()
		elif self.request.user.is_authenticated or user_checkout_id != None:
			user_can_continue = True
		else:
			pass
		if self.request.user.is_authenticated:
			#print("sdfasdkfbcsa dmnxfbcmszdbxfc jmszdbnx n,")
			user,created = UserCheckout.objects.get_or_create(email = self.request.user.email)
			user.user = self.request.user
			user.save()
			self.request.session['user_checkout_id'] = user.id
		context['user_can_continue'] = user_can_continue
		context['forms'] = form
		return context

	def post(self,request,*args,**kwargs):
		self.object = self.get_object()
		form = self.get_form()
		if form.is_valid():
			email = form.cleaned_data.get('email')
			user,created = UserCheckout.objects.get_or_create(email = email)
			request.session['user_checkout_id'] = user.id
			print(user , created)
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_success_url(self):
		return reverse('checkout')

	def get(self,request,*args,**kwargs):
		get_data = super(CheckOutView,self).get(request,*args,**kwargs)
		cart = self.get_object()
		checkout_id = request.session.get('user_checkout_id')
		if checkout_id != None:
			user_checkout = UserCheckout.objects.get(id = checkout_id)
			billing_id = request.session.get('billing_address_id')
			shipping_id = request.session.get('shipping_address_id')
			if billing_id == None or shipping_id == None:
				return redirect('checkout_address')
			else:
				b_address = UserAddress.objects.get(id=billing_id)
				s_address = UserAddress.objects.get(id=shipping_id)
			try:
				new_order_id = request.session.get("order_id")
				new_order = Order.objects.get(id = new_order_id)
			except:
				new_order = Order()
				request.session['order_id'] = new_order.id

			new_order.cart = cart
			new_order.user = user_checkout
			new_order.billing_address = b_address
			new_order.shipping_address = s_address
			new_order.save()
		return get_data
