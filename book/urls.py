
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
    path('login/',login,name='login'),
    path('logout/',logout_page,name='logout'),
    path('newacc/',newacc,name='newacc'),
    path('',dashboard,name='dashboard'),
    #path('base/',base),
    path('contact/',contact,name='contact'),
    path('selling/',selling,name='selling'),
    path('cart/add/<int:book_id>/', add_to_cart, name='add_to_cart'),
    path('cart/',view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/',remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_quantity, name='update_cart_quantity'),
    #path('services/',services,name='services'),
    path('books_display/',book,name='book'),
    path('payment/<int:book_id>/',payment, name='payment'),
    path('payment/success/<int:payment_id>/',success, name='success'),
    path('receipt/<int:payment_id>/', download_receipt, name='download_receipt'),
    path('checkout/success/', checkout_success, name='checkout_success'),
    path("ai/recommend/",ai_book_recommend, name="ai_book_recommend"),
    path('wishlist/toggle/<int:book_id>/', toggle_wishlist, name='toggle_wishlist'),

    path('notifications/', my_notifications, name='my_notifications'),
    path("reviews/", reviews_page, name="reviews"),
    path("submit-review/",submit_review, name="submit_review"),
    
    path('wishlist/',wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:book_id>/', add_to_wishlist, name='add_to_wishlist'),
    path("profile/", profile_view, name="profile"),
    path("edit-profile/",edit_profile, name="edit_profile"),

    
    path("edit-book/<int:book_id>/", edit_book, name="edit_book"),
    path("delete-book/<int:book_id>/",delete_book, name="delete_book"),

    path("search-suggest/", search_suggest, name="search_suggest"),
    path('wishlist/remove/<int:book_id>/', remove_from_wishlist, name='remove_from_wishlist'),




    path('checkout/', checkout, name='checkout'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

