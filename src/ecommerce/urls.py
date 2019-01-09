from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from newsletter.views import ( home,contact )
from carts.views import CartView
from .views import (about)
urlpatterns = [
    # Examples:
    url(r'^$',home , name='home'),
    url(r'^contact/$', contact , name='contact'),
    url(r'^about/$', about , name='about'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^product/',include('product.urls'),name="product"),
    url(r'^category/',include('product.url_categories'),name="product"),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^cart/$', CartView.as_view() , name="carts"),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)