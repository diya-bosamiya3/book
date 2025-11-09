from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from datetime import datetime
from xhtml2pdf import pisa
import requests
from openai import OpenAI
from book_app.models import *
from django.db.models import Q

client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def profile_view(request):
    user = request.user
    profile,created=Profile.objects.get_or_create(user=user)
    
    if request.method == "POST" and request.FILES.get("profile"):
        profile.profile = request.FILES["profile"]
        profile.save()
        return redirect("profile")
    # ✅ Orders placed by user (use buyer since Order has buyer FK)
    orders = Order.objects.filter(buyer=user).select_related("book")
    
    # ✅ Books sold by user (since your Book model uses `email` instead of seller FK)
    selling_books = Book.objects.filter(email=user.email)
    
    # ✅ Wishlist items
    wishlist = Wishlist.objects.filter(user=user).select_related("book")
    
    # ✅ Cart and items
    cart = Cart.objects.filter(user=user).first()
    cart_items = cart.items.select_related("book") if cart else []
    
    # ✅ Reviews written by user
    reviews = Review.objects.filter(user=user)
    
    # ✅ Login history
    login_history = LoginActivity.objects.filter(user=user).order_by("-login_time")
    
    # ✅ Payments (link is user → Payment, good)
    payments = Payment.objects.filter(user=user)

    return render(request, "profile.html", {
        "user": user,
        "profile": profile,
        "orders": orders,
        "selling_books": selling_books,
        "wishlist": wishlist,
        "cart_items": cart_items,
        "reviews": reviews,
        "login_history": login_history,
        "payments": payments,
    })



@login_required
def ai_book_recommend(request):
    user_query = request.GET.get("query", "")

    if not user_query:
        return JsonResponse({"reply": "Please ask something like: Suggest books similar to Atomic Habits."})

    # Fetch available books from your DB
    books = Book.objects.all().values("book_title", "author", "description")
    books_text = "\n".join([
        f"{b['book_title']} by {b['author']} — {b.get('description','')}"
        for b in books
    ])[:5000]  # prevent too long prompt

    prompt = f"""
You are an intelligent AI Book Recommendation Assistant.
User Query: {user_query}

Available Books in Store:
{books_text}

Suggest 5 books that match the user's interest.
Format response like this:

📘 **Book Name**
👨‍💻 Author
✨ Why recommended

If you find suitable suggestions from the user library, prioritize those.
Otherwise suggest globally popular books.
"""

    result = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = result.choices[0].message.content
    return JsonResponse({"reply": reply})


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            activity = LoginActivity.objects.create(user=user)
            request.session['login_activity_id'] = activity.id
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


def logout_page(request):
    activity_id = request.session.get('login_activity_id')
    if activity_id:
        try:
            activity = LoginActivity.objects.get(id=activity_id, user=request.user)
            activity.logout_time = now()
            activity.save()
        except LoginActivity.DoesNotExist:
            pass

    auth_logout(request)
    request.session.flush()
    return redirect('/')


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

        User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')

    return render(request, 'newacc.html')

@login_required
def dashboard(request):
    books = Book.objects.all()
    reviews = Review.objects.all().order_by('-created_at')[:5]

    # Get or create cart and count items
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_count = cart.items.count()

    return render(request, 'dashboard.html', {
        'books': books,
        'cart_count': cart_count,
        'reviews': reviews
    })

@login_required
def submit_review(request):
    if request.method == 'POST':
        rating = int(request.POST['rating'])
        comment = request.POST['comment']
        Review.objects.create(user=request.user, rating=rating, comment=comment)
        messages.success(request, 'Thanks for your review!')
        return redirect('dashboard')  # This will show it on the dashboard

    # If someone visits the page directly
    return render(request, 'reviews.html', {
        'reviews': Review.objects.order_by('-created_at')
    })

def review_page(request):
    return render(request,'reviews.html')


@login_required
def base(request):
    userinfo = LoginActivity.objects.filter(user=request.user).order_by('-id').first()
    profile,created=Profile.objects.get_or_create(user=request.user)
    return render(request, 'base.html', {'userinfo': userinfo, 'profile':profile})


def services(request):
    return render(request, 'services.html')


@login_required
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
    search = request.GET.get('search')
    
    if search:
        books = books.filter(
            Q(book_title__icontains=search) |
            Q(author__icontains=search)
        )

    # Suggestions (max 5)
    suggestions = Book.objects.filter(book_title__icontains=search)[:5] if search else []
    
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_count = cart.items.count()

    return render(request, 'books.html', {
        'books': books,
        'cart_count': cart_count,
        'suggestions': suggestions,  # ✅ fixed comma
        'search': search,  # ✅ send entered search text back
    })
from django.http import JsonResponse

@login_required
def search_suggest(request):
    term = request.GET.get("term", "")
    results = []

    if term:
        books = Book.objects.filter(book_title__icontains=term).values_list('book_title', flat=True)[:5]
        results = list(books)

    return JsonResponse(results, safe=False)


@login_required
def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            message=request.POST.get('message'),
            date=datetime.today()
        )
        messages.success(request, "Your message has been sent.")
    return render(request, 'contact.html')


@login_required
def add_to_cart(request, book_id):
    if request.method == "POST":
        book = get_object_or_404(Book, id=book_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        if not CartItem.objects.filter(cart=cart, book=book).exists():
            CartItem.objects.create(cart=cart, book=book)

        return HttpResponse(status=204)
    return HttpResponse(status=405)


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('book')
    total = sum(item.book.price for item in items)

    return render(request, 'view_cart.html', {'cart': cart, 'items': items, 'total': total})



@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum(item.book.price for item in items)

    if request.method == "POST":
        name = request.user.username  # Auto-filled name from logged-in user
        payment_method = request.POST.get('payment_method')
        card_num = request.POST.get('card_num')
        upi_id = request.POST.get('upi_id')
        address = request.POST.get('address')
        contact = request.POST.get('contact')

        if not name:
            return render(request, "checkout.html", {
                "items": items,
                "total": total,
                "error": "Name is required.",
            })

        # Create Payment record
        payment = Payment.objects.create(
            user=request.user,
            name=name,
            payment_method=payment_method,
            card_num=card_num if card_num else None,
            upi_id=upi_id if upi_id else None,
            address=address,
            contact=contact
        )

        # Create OrderedBook entries
        for item in items:
            OrderedBook.objects.create(
                payment=payment,
                book=item.book
            )
            item.book.is_sold = True  # Optional: track sold books
            item.book.save()

        # Clear the cart
        items.delete()

        return redirect("success", payment_id=payment.id)

    return render(request, "checkout.html", {
        "items": items,
        "total": total
    })

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.cart.user == request.user:
        item.delete()
    return redirect('view_cart')


@login_required
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


@login_required
def success(request, payment_id):
    payment = Payment.objects.get(id=payment_id, user=request.user)
    ordered_books = OrderedBook.objects.filter(payment=payment).select_related('book')

    return render(request, "success.html", {
        "payment": payment,
        "ordered_books": ordered_books
    })

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
    last_payment = Payment.objects.filter(name=request.user.username).last()
    return render(request, 'checkout_success.html', {'payment': last_payment})


@login_required
def submit_review(request):
    if request.method == 'POST':
        rating = int(request.POST['rating'])
        comment = request.POST['comment']
        Review.objects.create(user=request.user, rating=rating, comment=comment)
        return render(request, 'reviews.html', {
            'message': 'Thank you for your review!',
            'reviews': Review.objects.order_by('-created_at')
        })
    return render(request, 'reviews.html', {
        'reviews': Review.objects.order_by('-created_at')
    })


@require_POST
@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    return HttpResponse(status=204)

@login_required
def remove_from_wishlist(request, book_id):
    Wishlist.objects.filter(user=request.user, book_id=book_id).delete()
    return redirect('wishlist_view')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('book')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})