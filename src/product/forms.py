from django import forms
from django.forms.models import modelformset_factory
from .models import Variation


class VariationListForm(forms.ModelForm):
	class Meta:
		model = Variation
		fields = [
			'title',
			'price',
			'inventory',
			'active'
		]

VariationInventoryFormSet = modelformset_factory(Variation,form=VariationListForm,extra=0)