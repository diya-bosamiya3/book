from django.contrib import admin
from book_app.models import LoginActivity,Contact,Nuser,Book,Payment,Cart,CartItem



admin.site.register(Contact)
admin.site.register(Payment)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Book)
admin.site.register(LoginActivity)
admin.site.register(Nuser)
