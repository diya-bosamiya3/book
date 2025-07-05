from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User
from book_app.models import LoginActivity,Contact,NewUser,Book
from django.utils.timezone import now
from datetime import datetime
from django.contrib import messages


def login(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request,'You dont have account here,Please make new Account!')
            return redirect('newacc')

        
        user=authenticate(request,username=username,password=password)
        
        if user is not None:
            LoginActivity.objects.create(username=user.username, email=user.email, login_time=now())
            auth_login(request,user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

       

from django.contrib.auth import login as auth_login  # for automatic login after registration

def newacc(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        
        # Check if user already exists
        if password!=confirm_password:
            messages.error(request,"Confirm password does not match the password")
            return render(request, 'newacc.html')
        
            
        user=User.objects.create_user(
        username=username,
        email=email,
        password=password
        )
        user.save()   

        new_user=NewUser(username=username, email=email,login_time=now())
        new_user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')  # redirect to login page after registration

    return render(request, 'newacc.html')


def dashboard(request):
    books = Book.objects.all().order_by('-id')  # latest first
    print(books)
    return render(request, 'dashboard.html', {'books': books})
    
def base(request):
    return render(request,'base.html')

def services(request):
    return render(request,'services.html')

def buy_book_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_app/payment.html', {'book': book})
def payment(request):
    return render(request,'payment.html')


def selling(request):
    if request.method == "POST":
        book = Book(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            book_title=request.POST.get('title'),
            author=request.POST.get('author'),
            condition=request.POST.get('condition'),
            price=request.POST.get('price'),
            book_photo=request.FILES.get('photo'),
            description=request.POST.get('description')
        )
        book.save()
        return redirect('dashboard')
    return render(request, 'selling.html')

def contact(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        message=request.POST.get('message')
        contact=Contact(name=name,email=email,phone=phone,message=message,date=datetime.today())
        contact.save()
        messages.success(request, "Your message has been sent.")
        
    return render(request,'contact.html')



def booksel(request):
    return render(request,'booksel.html')
