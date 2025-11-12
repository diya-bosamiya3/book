from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Nuser, LoginActivity, Book, Contact, Payment, 
    Cart, CartItem, OrderedBook, Order, Wishlist, Review,Notification
)

# Unregister and re-register the built-in User with custom admin
if admin.site.is_registered(User):
    admin.site.unregister(User)

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
    ordering = ('-id',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'message', 'date')
    ordering = ('-date',)
    search_fields = ('name', 'email')

class OrderedBookInline(admin.TabularInline):
    model = OrderedBook
    extra = 0

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'name', 'payment_method',
        'card_num', 'upi_id', 'address', 'contact'
    )
    ordering = ('-id',)
    search_fields = ('user__username', 'name')
    inlines = [OrderedBookInline]

@admin.register(OrderedBook)
class OrderedBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'book')
    search_fields = ('book__book_title',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book_count')

    def book_count(self, obj):
        return obj.items.count()
    book_count.short_description = 'Books in Cart'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'book')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'book', 'quantity', 'total_price', 'payment_mode', 'status', 'order_date')
    list_filter = ('status', 'payment_mode')
    search_fields = ('buyer__username', 'book__book_title')
    ordering = ('-order_date',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'added_at')
    search_fields = ('user__username', 'book__book_title')
    ordering = ('-added_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'comment', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'comment')
    ordering = ('-created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)

