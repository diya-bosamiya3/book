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
from book_app.views import login,newacc,dashboard,base,contact,booksel,selling,services,payment
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Admin Page"
admin.site.site_title = "Managing system"
admin.site.index_title = "Welcome to the managing page"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login,name='login'),
    path('newacc/',newacc,name='newacc'),
    path('dashboard/',dashboard,name='dashboard'),
    path('base/',base),
    path('contact/',contact,name='contact'),
    path('selling/',selling,name='selling'),
    path('booksel/',booksel,name='booksel'),
    path('services/',services,name='services'),
    path('payment/',payment,name='payment'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

