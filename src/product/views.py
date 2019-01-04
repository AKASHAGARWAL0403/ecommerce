from django.shortcuts import render , get_object_or_404 , redirect , Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib import messages
from django.db.models import Q
# Create your views here.
from .models import (Product,Variation)
from django.utils import timezone
from .forms import VariationInventoryFormSet

class VariationListView(ListView):
	model = Variation
	queryset = Variation.objects.all()

	def get_context_data(self,*args,**kwargs):
		query = super(VariationListView,self).get_context_data(*args,**kwargs)
		query["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
		return query

	def get_queryset(self,*args,**kwargs):
		product_pk = self.kwargs.get("pk")
		if product_pk:
			pro = get_object_or_404(Product,pk=product_pk)
			queryset = Variation.objects.filter(product = pro)
		return queryset

	def post(self, request, *args, **kwargs):
		formset = VariationInventoryFormSet(request.POST,request.FILES)
		print(request.POST)
		print("akdwsxc szcxm")
		print(formset.is_valid())
		if formset.is_valid():
			formset.save(commit=False)
			for form in formset:
				new_item = form.save(commit=False)
				product_pk = self.kwargs.get("pk")
				product = get_object_or_404(Product, pk=product_pk)
				new_item.product = product
				new_item.save()
				
			messages.success(request, "Your inventory and pricing has been updated.")
			return redirect("product_list")
		raise Http404


class ProductDetailView(DetailView):
	model = Product


class ProductListView(ListView):
	model = Product
	queryset = Product.objects.all()
   
	def get_context_data(self,*args, **kwargs):
		context = super(ProductListView,self).get_context_data(*args,**kwargs)
		context['now'] = timezone.now()
		context['query'] = self.request.GET.get('q')
		return context


	def get_queryset(self,*args,**kwargs):
		query = super(ProductListView,self).get_queryset(*args,**kwargs)
		qs = self.request.GET.get("q")
		if qs:
			query = self.model.objects.filter(
						Q(title__icontains=qs) | 
						Q(description__icontains=qs)
					)
			try:
				query2 = self.model.objects.filter(
						Q(price=qs)
					)
				query = query | query2
			except:
				pass

		return query