from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from book_app.models import Nuser, LoginActivity, Book, Contact,Payment
from django.http import HttpRequest,HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
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

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('newacc')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        return redirect('login')

    return render(request, 'newacc.html')

@login_required(login_url="/")
def dashboard(request):
    return render(request,"dashboard.html")

def base(request):
    userinfo=LoginActivity.objects.get()
    return render(request,'base.html',{
        'userinfo':userinfo
    })

def services(request):
    return render(request,'services.html')

@login_required(login_url="/")
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

@login_required(login_url="/")
def book_display(request):
    books = Book.objects.all().order_by('-id')
    return render(request, 'books.html', {
        'books': books,
    })

@login_required(login_url="/")
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

@login_required(login_url="/")
def payment(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        method = request.POST.get("payment_method")
        name = request.POST.get("name")
        card_num = request.POST.get("card_num")
        expiry = request.POST.get("expiry")
        cvv = request.POST.get("cvv")
        upi_id = request.POST.get("upi_id")
        address = request.POST.get("address")
        contact = request.POST.get("contact")

        payment_obj = Payment.objects.create(
            book=book,
            name=name,
            payment_method=method,
            card_num=card_num if method == "credit" else None,
            expiry=expiry if method == "credit" else None,
            cvv=cvv if method == "credit" else None,
            upi_id=upi_id if method == "upi" else None,
            address=address if method == "cash" else None,
            contact=contact if method == "cash" else None,
        )

        return redirect('success', payment_id=payment_obj.id)

    return render(request, "payment.html", {"book": book})


def success(request, payment_id):
    order = get_object_or_404(Payment, id=payment_id)
    return render(request, 'success.html', {'order': order})

def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    template_path = 'receipt.html'
    context = {'order': payment}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_Order_{payment.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors while generating the receipt.')
    return response