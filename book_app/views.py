from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from book_app.models import Nuser, LoginActivity, Book, Contact,Payment,Cart,CartItem
from django.http import HttpRequest,HttpResponse
from openai import OpenAI
import requests

from django.conf import settings
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required


client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def ai_book_suggestions(request):
    query = "science fiction"  # You can dynamically change this
    response = requests.get(f"https://openlibrary.org/search.json?q={query}")
    
    if response.status_code == 200:
        data = response.json()
        books = data.get('docs', [])[:5]  # Get top 5 books
        suggestions = [
            f"{book.get('title')} by {', '.join(book.get('author_name', ['Unknown']))}"
            for book in books
        ]
    else:
        suggestions = ["Failed to fetch suggestions. Try again later."]

    return render(request, 'ai_suggestions.html', {'suggestions': suggestions})
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

@login_required
def dashboard(request):
    books = Book.objects.all()

    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.count()

    return render(request, 'dashboard.html', {
        'books': books,
        'cart_count': cart_count,
    })

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

@login_required
def book_display(request):
    books = Book.objects.all().order_by('-id')

    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.count()

    return render(request, 'books.html', {
        'books': books,
        'cart_count': cart_count,
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



@login_required
def add_to_cart(request, book_id):
    if request.method == "POST":
        book = get_object_or_404(Book, id=book_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        if not CartItem.objects.filter(cart=cart, book=book).exists():
            CartItem.objects.create(cart=cart, book=book)

        return HttpResponse(status=204)  # Empty response for iframe

    return HttpResponse(status=405)

@login_required
def view_cart(request):
    # Get or create the cart for the current user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Fetch all items
    items = cart.items.select_related('book')  # Optimized query

    total = sum(item.book.price for item in items)

    return render(request, 'view_cart.html', {
        'cart': cart,
        'items': items,
        'total': total,
    })

@login_required
def checkout(request):
    cart = Cart.objects.get_or_create(user=request.user)[0]
    items = CartItem.objects.filter(cart=cart)

    if request.method == "POST":
        name = request.user.username
        payment_method = request.POST.get("payment_method")
        card_num = request.POST.get("card_num")
        expiry = request.POST.get("expiry")
        cvv = request.POST.get("cvv")
        upi_id = request.POST.get("upi_id")
        address = request.POST.get("address")
        contact = request.POST.get("contact")

        for item in items:
            Payment.objects.create(
                book=item.book,
                name=name,
                payment_method=payment_method,
                card_num=card_num if payment_method == 'credit' else '',
                expiry=expiry if payment_method == 'credit' else '',
                cvv=cvv if payment_method == 'credit' else '',
                upi_id=upi_id if payment_method == 'upi' else '',
                address=address,
                contact=contact
            )

        # Clear cart after checkout
        items.delete()
        messages.success(request, "Payment successful for all books!")
        return redirect('checkout_success')
  # Or dashboard

    total = sum(item.book.price for item in items)
    return render(request, 'checkout.html', {'items': items, 'total': total})

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.cart.user == request.user:
        item.delete()

    return redirect('view_cart')  # Make sure you have this view and template

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

@login_required
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
        return HttpResponse('Error generating receipt.')
    return response

@login_required
def checkout_success(request):
    # Get the latest payment by this user (optional but useful)
    last_payment = Payment.objects.filter(name=request.user.username).last()
    return render(request, 'checkout_success.html', {'payment': last_payment})
