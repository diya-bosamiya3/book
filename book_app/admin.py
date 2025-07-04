from django.contrib import admin
from book_app.models import LoginActivity,Contact,NewUser,Book


# Register your models here.


admin.site.register(Contact)


admin.site.register(Book)
admin.site.register(LoginActivity)
admin.site.register(NewUser)
