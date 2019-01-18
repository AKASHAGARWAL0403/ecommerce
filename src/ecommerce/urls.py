from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from newsletter.views import ( home,contact )
from carts.views import CartView , ItemCount , CheckOutView , CheckoutFinalView
from .views import (about)
from orders.views import AddressSelectFormView , UserAddressCreateView , OrderList , OrderDetail

urlpatterns = [
    # Examples:
    url(r'^$',home , name='home'),
    url(r'^contact/$', contact , name='contact'),
    url(r'^about/$', about , name='about'),
    url(r'^orders/(?P<pk>\d+)/$',OrderDetail.as_view(),name='order_detail'),
    url(r'^orders/$',OrderList.as_view(),name='order_list'),
   
    # url(r'^blog/', include('blog.urls')),
    url(r'^product/',include('product.urls'),name="product"),
    url(r'^category/',include('product.url_categories'),name="product"),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^cart/count/$', ItemCount.as_view() , name="cart_count"),
    url(r'^cart/$', CartView.as_view() , name="carts"),
    url(r'^checkout/$', CheckOutView.as_view() , name="checkout"),
    url(r'^checkout/address/$', AddressSelectFormView.as_view() , name="checkout_address"),
    url(r'^checkout/address/add/$', UserAddressCreateView.as_view(), name='user_address_create'),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name='checkout_final'),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)