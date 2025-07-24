from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Nuser, LoginActivity, Book, Contact, Payment, Cart, CartItem, Order

# Unregister default User admin if already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active', 'date_joined')
    ordering = ('-date_joined',)
    search_fields = ('username', 'email')

admin.site.register(User, CustomUserAdmin)

@admin.register(Nuser)
class NuserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'password')

@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'login_time', 'logout_time')
    ordering = ('-login_time',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_title', 'author', 'price', 'condition', 'email', 'phone')
    search_fields = ('book_title', 'author')
    ordering = ('book_title',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'message', 'date')
    ordering = ('-date',)
    search_fields = ('name', 'email')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_user', 'get_book', 'get_payment_method',
        'get_card_num', 'get_upi_id', 'get_address', 'get_contact'
    )
    ordering = ('-id',)

    def get_user(self, obj):
        return obj.order.user.username
    get_user.short_description = 'User'

    def get_book(self, obj):
        return obj.book.book_title
    get_book.short_description = 'Book'

    def get_payment_method(self, obj):
        return obj.order.payment_method
    get_payment_method.short_description = 'Method'

    def get_card_num(self, obj):
        return obj.order.card_num
    get_card_num.short_description = 'Card Number'

    def get_upi_id(self, obj):
        return obj.order.upi_id
    get_upi_id.short_description = 'UPI ID'

    def get_address(self, obj):
        return obj.order.address
    get_address.short_description = 'Address'

    def get_contact(self, obj):
        return obj.order.contact
    get_contact.short_description = 'Contact'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'book')

# Optional: Register Order model for completeness
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_method', 'created_at')
    ordering = ('-created_at',)
