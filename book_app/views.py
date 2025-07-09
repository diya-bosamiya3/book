from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from book_app.models import Nuser, LoginActivity, Book, Contact
from django.http import HttpRequest,HttpResponse

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # ✅ Check if user exists in Nuser model (not LoginActivity)
        try:
            user = Nuser.objects.get(username=username)
        except Nuser.DoesNotExist:
            messages.error(request, 'You don’t have an account here. Please create one!')
            return redirect('newacc')

        # ✅ Check if password matches
        if user.password == password:
            # ✅ Log activity
            LoginActivity.objects.create(
                username=user.username,
                email=user.email,
                login_time=datetime.now()
            )

           
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid password.")
            return redirect('login')

    return render(request, 'login.html')
def newacc(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('newacc')


        user = Nuser(username=username, email=email, password=password)
        print(username,email,password)
        user.save()

        # Also store to LoginActivity
        LoginActivity.objects.create(
            username=username,
            email=email,
            login_time=datetime.now()
        )

        
        return redirect('dashboard')

    return render(request, 'newacc.html')

def dashboard(request):
    return render(request,"dashboard.html")

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
        return redirect('book')
    return render(request, 'selling.html')

def book_display(request):
    books = Book.objects.all().order_by('-id')
    return render(request, 'books.html', {
        'books': books,
    })


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

