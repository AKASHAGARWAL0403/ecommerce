from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import post_save
# Create your models here.

class ProductQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)

class ProductManager(models.Manager):
	def get_queryset(self):
		return ProductQuerySet(self.model, using=self._db)

	def all(self,*args,**kwargs):
		return self.get_queryset().active()

	def get_related(self,instance):
		product_one = self.get_queryset().filter(categories__in=instance.categories.all())
		product_two = self.get_queryset().filter(default=instance.default)
		result = (product_one | product_two).exclude(id=instance.id).distinct()
		return result


class Product(models.Model):
	title = models.CharField(max_length=120)
	description = models.TextField(blank=True, null=True)
	price = models.DecimalField(decimal_places=2, max_digits=20)
	active = models.BooleanField(default=True)
	categories = models.ManyToManyField('Category', blank=True)
	default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True,on_delete=models.CASCADE)


	objects = ProductManager()

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("product_detail",kwargs={"pk":self.pk})

	def get_image_url(self):
		img = self.productimage_set.first()
		if img:
			return img.image.url
		else:
			return img

class Variation(models.Model):
	product = models.ForeignKey(Product,on_delete=models.CASCADE)
	title = models.CharField(max_length=120)
	price = models.DecimalField(decimal_places=2, max_digits=20)
	sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
	active = models.BooleanField(default=True)
	inventory = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return self.product.title

	def get_price(self):
		if self.sale_price is not None:
			return self.sale_price
		else:
			return self.price

	def get_absolute_url(self):
		return self.product.get_absolute_url()

	def get_title(self):
		return "%s - %s" %(self.product.title , self.title)

	def add_to_cart(self):
		return "%s?item=%s&qty=1" %(reverse('carts'),self.id)

	def remove_from_cart(self):
		return "%s?item=%s&qty=1&delete=True" %(reverse('carts'),self.id)

def post_reciever_veriation_product(sender,instance,created,*args,**kwargs):
	product = instance
	variations = instance.variation_set.all()
	if variations.count() == 0:
		new_var = Variation()
		new_var.product = product
		new_var.title = "DEFAULT"
		new_var.price = instance.price
		new_var.save()

post_save.connect(post_reciever_veriation_product,sender=Product) 

def upload_to_image(instance,filename):
	title = instance.product.title
	slug = slugify(title)
	basename, file_extension = filename.split(".")
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extension)
	return "products/%s/%s" %(slug, new_filename)



class ProductImage(models.Model):
	product = models.ForeignKey(Product,on_delete=models.CASCADE)
	image = models.ImageField(upload_to=upload_to_image)

	def __str__(self):
		return self.product.title


class Category(models.Model):
	title = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(unique=True)
	description = models.TextField(null=True, blank=True)
	active = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __str__(self):
		return self.title


	def get_absolute_url(self):
		return reverse("category_detail", kwargs={"slug": self.slug })

def image_upload_to_featured(instance, filename):
	title = instance.product.title
	slug = slugify(title)
	basename, file_extension = filename.split(".")
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extension)
	return "products/%s/featured/%s" %(slug, new_filename)




class ProductFeatured(models.Model):
	product = models.ForeignKey(Product,on_delete=models.CASCADE)
	image = models.ImageField(upload_to=image_upload_to_featured)
	title = models.CharField(max_length=120, null=True, blank=True)
	text = models.CharField(max_length=220, null=True, blank=True)
	text_right = models.BooleanField(default=False)
	text_css_color = models.CharField(max_length=6, null=True, blank=True)
	show_price = models.BooleanField(default=False)
	make_image_background = models.BooleanField(default=False)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.product.title
