"""
URL configuration for book project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from book_app.views import *
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Admin Page"
admin.site.site_title = "Managing system"
admin.site.index_title = "Welcome to the managing page"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login,name='login'),
    path('logout/',logout_page,name='logout'),
    path('newacc/',newacc,name='newacc'),
    path('dashboard/',dashboard,name='dashboard'),
    path('base/',base),
    path('contact/',contact,name='contact'),
    path('selling/',selling,name='selling'),
    path('cart/add/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('cart/',view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/',remove_from_cart, name='remove_from_cart'),
    path('services/',services,name='services'),
    path('books_display/',book_display,name='book'),
    path('payment/<int:book_id>/',payment, name='payment'),
    path('payment/success/<int:payment_id>/',success, name='success'),
    path('receipt/<int:payment_id>/', download_receipt, name='download_receipt'),
    path('checkout/success/', checkout_success, name='checkout_success'),
    path('ai-suggestions/', ai_book_suggestions, name='ai_suggestions'),
    path('reviews/',submit_review, name='submit_review'),
    path('wishlist/',wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:book_id>/', add_to_wishlist, name='add_to_wishlist'),

    path('wishlist/remove/<int:book_id>/', remove_from_wishlist, name='remove_from_wishlist'),




    path('checkout/', checkout, name='checkout'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

