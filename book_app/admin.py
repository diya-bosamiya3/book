from django.contrib import admin
from book_app.models import LoginActivity,Contact,NewUser,Book

class Userr(admin.ModelAdmin):
    list_display=('username','email','password')
# Register your models here.


admin.site.register(Contact)


admin.site.register(Book)
admin.site.register(LoginActivity)
admin.site.register(NewUser,Userr)
