from django.shortcuts import render
from .forms import AddressForm
from django.views.generic.edit import FormView
from .forms import AddressForm
from .models import UserAddress , UserCheckout
# Create your views here.

class AddressSelectFormView(FormView):
	form_class = AddressForm
	template_name = "orders/address_select.html"


	def get_address(self):
		user_checkout_id = self.request.session.get('user_checkout_id')
		user = UserCheckout.objects.get(id = user_checkout_id)
		b_address = UserAddress.objects.filter(
				user = user,
				type='billing'
			)
		s_address = UserAddress.objects.filter(
				user = user,
				type = 'shipping'
			)
		return b_address,s_address

	def get_form(self,*args,**kwrags):
		form = super(AddressSelectFormView,self).get_form(*args,*kwrags)
		b_address , s_address = self.get_address()

		form.fields['billing_address'].queryset = b_address
		form.fields['shipping_address'].queryset = s_address

		return form

	def form_valid(self,form , *args,**kwargs):
		billing_address = form.cleaned_data['billing_address']
		shipping_address = form.cleaned_data['shipping_address']
		self.request.session['billing_address_id'] = billing_address.id
		self.request.session['shipping_address_id'] = shipping_address.id
		return super(AddressSelectFormView,self).form_valid(form ,*args,*kwargs)

	def get_success_url(self, *args, **kwargs):
		return "/checkout/"