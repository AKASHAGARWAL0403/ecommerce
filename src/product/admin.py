from django.contrib import admin
from .models import Product , ProductImage , Variation , Category , ProductFeatured
# Register your models here.

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Variation)
admin.site.register(Category)
admin.site.register(ProductFeatured)