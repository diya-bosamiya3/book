from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Case, When, IntegerField
from django.db import transaction
from datetime import timedelta
import google.generativeai as genai
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import*
from django.db.models import F, FloatField, ExpressionWrapper
from django.views.decorators.csrf import csrf_exempt
import json
genai.configure(api_key="YOUR_GEMINI_API_KEY")

@login_required
def ai_book_recommend(request):
    query = request.GET.get("q", "")

    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)

    try:
        model = genai.GenerativeModel("gemini-pro")

        response = model.generate_content(
            f"Suggest books for: {query}. Give short, clear suggestions only."
        )

        return JsonResponse({
            "recommendation": response.text
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# ============================
#  🔥 UNIVERSAL HELPER UTILS
# ============================

def run_auto_hide_cleanup():
    """Auto-hide books that stayed out of stock for 1 hour."""
    cutoff = timezone.now() - timedelta(hours=1)
    Book.objects.filter(out_of_stock_time__lte=cutoff, is_sold=False).update(is_sold=True)


def is_book_visible(book):
    """Check whether book should be shown before it fully disappears after 1 hour."""
    if book.quantity > 0:
        return True
    
    if book.quantity == 0 and book.out_of_stock_time:
        return timezone.now() <= book.out_of_stock_time + timedelta(hours=1)

    return False


def get_wishlist_ids(user):
    return list(Wishlist.objects.filter(user=user).values_list("book_id", flat=True))




def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            activity = LoginActivity.objects.create(user=user, username=user.username, email=user.email)
            request.session["login_activity_id"] = activity.id
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

def newacc(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("newacc")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect("newacc")

        # Check password confirm
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("newacc")

        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "newacc.html")

def logout(request):
    activity_id = request.session.get("login_activity_id")
    if activity_id:
        try:
            activity = LoginActivity.objects.get(id=activity_id, user=request.user)
            activity.logout_time = timezone.now()
            activity.save()
        except:
            pass

    auth_logout(request)
    request.session.flush()
    return redirect("dashboard")

@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)  # ensure profile object

    selling_books = Book.objects.filter(seller=user, is_sold=False)
    sold_books = Book.objects.filter(seller=user, is_sold=True)
    wishlist_items = Wishlist.objects.filter(user=user).select_related("book")

    context = {
        "user": user,
        "profile": profile,  # add this
        "selling_books": selling_books,
        "sold_books": sold_books,
        "wishlist_items": wishlist_items,
    }
    return render(request, "profile.html", context)
@login_required
def edit_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        profile_pic = request.FILES.get("profile")

        user.username = username
        user.email = email
        user.save()

        if profile_pic:
            profile.profile = profile_pic
            profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile_view")

    return render(request, "edit_profile.html", {"user": user, "profile": profile})

# =======================
#  PROFILE
# =======================
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    selling_books = Book.objects.filter(seller=request.user, is_sold=False)

    # Orders received
    orders_received = OrderedBook.objects.filter(
        book__seller=request.user
    ).select_related("book", "payment", "payment__user")

    # --- CART COUNT ---
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_count = cart_items.count()
    except Cart.DoesNotExist:
        cart_items = []
        cart_count = 0

    # --- WISHLIST COUNT ---
    wishlist_items = Wishlist.objects.filter(user=request.user)
    wishlist_count = wishlist_items.count()

    context = {
        "profile": profile,
        "selling_books": selling_books,
        "sold_orders": orders_received,
        "orders": Order.objects.filter(buyer=request.user),

        # ⭐ VERY IMPORTANT
        "cart_items": cart_items,
        "cart_count": cart_count,

        "wishlist": wishlist_items,
        "wishlist_count": wishlist_count,

        "reviews": Review.objects.filter(user=request.user),
    }

    return render(request, "profile.html", context)



@login_required
def edit_book(request, book_id):
    # ensures only owner can edit
    book = get_object_or_404(Book, id=book_id, seller=request.user)

    if request.method == "POST":
        # get values
        title = request.POST.get("book_title", "").strip()
        author = request.POST.get("author", "").strip()
        price_raw = request.POST.get("price", "").strip()
        qty_raw = request.POST.get("quantity", "0").strip()

        # basic validation / casting
        try:
            price = float(price_raw) if price_raw != "" else book.price
        except ValueError:
            messages.error(request, "Invalid price value.")
            return redirect("edit_book", book_id=book_id)

        try:
            quantity = int(qty_raw)
            if quantity < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Quantity must be a non-negative integer.")
            return redirect("edit_book", book_id=book_id)

        # assign
        book.book_title = title or book.book_title
        book.author = author or book.author
        book.price = price
        book.quantity = quantity

        if request.FILES.get("book_photo"):
            book.book_photo = request.FILES["book_photo"]

        book.save()
        messages.success(request, "Book updated successfully.")
        return redirect("profile")  # use your named profile url

    return render(request, "edit_book.html", {"book": book})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, seller=request.user)
    book.delete()
    return redirect("profile_view")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email    = request.POST.get("email").strip()
        password = request.POST.get("password")
        confirm  = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "register.html")


# =======================
#  DASHBOARD + BOOK DISPLAY
# =======================

def dashboard(request):
    run_auto_hide_cleanup()

    # All available books for homepage sections
    books = Book.objects.filter(is_sold=False).order_by("-id")

    # 🔥 Top 5 Trending Books (recently added)
    top_books = Book.objects.filter(is_sold=False).order_by("-id")[:5]

    # 🌟 Latest Reviews
    reviews = Review.objects.all().order_by("-created_at")[:6]

    context = {
        "books": books,
        "top_books": top_books,
        "reviews": reviews,
    }

    # 🛒 If user logged in → cart, wishlist, notifications
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        context["cart_count"] = cart.items.count()
        context["wishlist_ids"] = get_wishlist_ids(request.user)

        context["unread_notifications"] = (
            request.user.notifications.filter(is_read=False).count()
        )
    else:
        # Required to prevent crash for anonymous users
        context["unread_notifications"] = 0

    return render(request, "dashboard.html", context)


def book(request):
    run_auto_hide_cleanup()

    search = request.GET.get("search", "").strip()
    one_hour_ago = timezone.now() - timedelta(hours=1)

    qs = Book.objects.filter(
        Q(quantity__gt=0) |
        Q(quantity=0, out_of_stock_time__gte=one_hour_ago),
        is_sold=False
    )

    if search:
        qs = qs.filter(
            Q(book_title__icontains=search) |
            Q(author__icontains=search)
        )

    # Annotate queryset with in-stock ordering
    qs = qs.annotate(
        in_stock_order=Case(
            When(quantity__gt=0, then=1),
            default=0,
            output_field=IntegerField()
        ),
        # Annotate a new field for price including 30% profit
        price_with_profit=ExpressionWrapper(
            F('price') * 1.3,
            output_field=FloatField()
        )
    ).order_by("-in_stock_order", "-id")

    # ----- USER INFO ONLY IF LOGGED IN -----
    cart_count = 0
    wishlist_ids = []

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.count()
        wishlist_ids = get_wishlist_ids(request.user)

    return render(request, "books.html", {
        "books": qs,
        "search": search,
        "cart_count": cart_count,
        "wishlist_ids": wishlist_ids,
    })
# =======================
#  SELLING
# =======================

@login_required
def selling(request):
    if request.method == "POST":
        Book.objects.create(
            seller=request.user,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            book_title=request.POST.get("title"),
            author=request.POST.get("author"),
            condition=request.POST.get("condition"),
            price=request.POST.get("price"),
            book_photo=request.FILES.get("photo"),
            description=request.POST.get("description"),
            quantity=int(request.POST.get("quantity") or 1)
        )
        return redirect("profile")

    return render(request, "selling.html")

@login_required
@csrf_exempt
def update_cart_quantity(request, item_id):
    if request.method == "POST":
        data = json.loads(request.body)
        qty = max(1, int(data.get("quantity", 1)))
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        if qty > item.book.quantity:
            qty = item.book.quantity
        item.quantity = qty
        item.save()
        return JsonResponse({"status": "ok", "quantity": qty})
    return JsonResponse({"error": "invalid request"}, status=400)
# =======================
#  CART
# =======================
def add_to_cart(request, book_id):
    if request.method != "POST":
        return HttpResponse(status=405)

    run_auto_hide_cleanup()
    book = get_object_or_404(Book, id=book_id)

    if not is_book_visible(book):
        return JsonResponse({"error": "out_of_stock"}, status=400)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    quantity = int(request.POST.get("quantity", 1))

    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    if created:
        # First time adding this book
        cart_item.quantity = quantity
    else:
        # Already exists → increase quantity
        cart_item.quantity += quantity

    cart_item.save()

    return redirect("book")


def cart_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(cart__user=request.user).count()
    else:
        count = 0
    return {"cart_count": count}


def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        count = 0
    return {"wishlist_count": count}

@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("book")

    total = sum(item.total_price for item in items)  # uses property with profit

    return render(
        request,
        "cart.html",
        {
            "items": items,
            "total": total,
            "cart_count": items.count(),
        }
    )


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect("view_cart")


# =======================
#  CHECKOUT
# =======================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Cart, CartItem, Book, Payment, OrderedBook, Notification


@login_required
def checkout(request):
    run_auto_hide_cleanup()
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related("book")

    total = sum(item.total_price for item in items)

    DELIVERY_CHARGES = 60
    PLATFORM_FEES = 20
    total_with_fees = total + DELIVERY_CHARGES + PLATFORM_FEES

    if request.method == "POST":
        unavailable = [i.book.book_title for i in items if not is_book_visible(i.book)]
        if unavailable:
            return render(request, "checkout.html", {
                "items": items,
                "total": total_with_fees,
                "delivery_charges": DELIVERY_CHARGES,
                "platform_fees": PLATFORM_FEES,
                "error": "Unavailable: " + ", ".join(unavailable)
            })

        with transaction.atomic():
            payment = Payment.objects.create(
                user=request.user,
                name=request.user.username,
                payment_method=request.POST.get("payment_method"),
                card_num=request.POST.get("card_num") or None,
                upi_id=request.POST.get("upi_id") or None,
                address=request.POST.get("address"),
                contact=request.POST.get("contact"),
                delivery_charges=DELIVERY_CHARGES,
                platform_fees=PLATFORM_FEES,
                total_amount=total_with_fees
            )

            for item in items:
                book = Book.objects.select_for_update().get(id=item.book.id)
                OrderedBook.objects.create(payment=payment, book=book, quantity=item.quantity)

                book.quantity -= item.quantity
                if book.quantity <= 0:
                    book.quantity = 0
                    if not book.out_of_stock_time:
                        book.out_of_stock_time = timezone.now()
                    book.is_sold = True
                book.save()

                if book.seller:
                    Notification.objects.create(
                        user=book.seller,
                        message=f"{request.user.username} ordered your book '{book.book_title}'"
                    )

            items.delete()

        return redirect("success", payment_id=payment.id)

    return render(request, "checkout.html", {
        "items": items,
        "total": total_with_fees,
        "delivery_charges": DELIVERY_CHARGES,
        "platform_fees": PLATFORM_FEES
    })

@login_required
def success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    ordered_books = OrderedBook.objects.select_related("book").filter(payment=payment)

    # Prepare book details including image
    books_total = Decimal(0)
    book_details = []

    for item in ordered_books:
        price_per_book = item.book.price * Decimal('1.3')  # if you want to include profit
        total_for_item = price_per_book * item.quantity
        books_total += total_for_item

        # Add photo URL or default
        photo_url = item.book.book_photo.url if item.book.book_photo else '/static/book_app/default-book.png'

        book_details.append({
            "title": item.book.book_title,
            "author": item.book.author,
            "quantity": item.quantity,
            "price_per_book": price_per_book,
            "total_for_item": total_for_item,
            "photo_url": photo_url
        })

    delivery_charges = payment.delivery_charges or 0
    platform_fees = payment.platform_fees or 0
    grand_total = books_total + Decimal(delivery_charges) + Decimal(platform_fees)

    context = {
        "payment": payment,
        "ordered_books": book_details,
        "books_total": books_total,
        "delivery_charges": delivery_charges,
        "platform_fees": platform_fees,
        "grand_total": grand_total,
    }

    return render(request, "success.html", context)


# ===========================
#  AUTH EXTRA VIEWS
# ===========================

def logout_page(request):
    return logout(request)   # reuse existing logout()


# ===========================
#  BOOK DISPLAY
# ===========================




# ===========================
#  PAYMENT + RECEIPT
# ===========================
@login_required
def toggle_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    exists = Wishlist.objects.filter(user=request.user, book=book)

    if exists:
        exists.delete()
        return JsonResponse({"status": "removed"})
    else:
        Wishlist.objects.create(user=request.user, book=book)
        return JsonResponse({"status": "added"})


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, "wishlist.html", {"wishlist_items": wishlist_items})


@login_required
def add_to_wishlist(request, book_id):
    Wishlist.objects.get_or_create(user=request.user, book_id=book_id)
    return redirect("wishlist_view")


@login_required
def remove_from_wishlist(request, book_id):
    Wishlist.objects.filter(user=request.user, book_id=book_id).delete()
    return redirect("wishlist_view")


@login_required
def my_notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_notifications.html", {"notifications": notes})


def submit_review(request):
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not rating:
            messages.error(request, "Please select a star rating.")
            return redirect("reviews")

        Review.objects.create(
            user=request.user,
            rating=int(rating),
            comment=comment,
        )

        messages.success(request, "Thank you for your review!")
        return redirect("reviews")

    return redirect("reviews")

def reviews_page(request):
    all_reviews = Review.objects.order_by("-created_at")

    context = {
        "reviews": all_reviews,
        "message": None,
    }

    # Pass Django's messages into your template's "message"
    storage = messages.get_messages(request)
    for msg in storage:
        context["message"] = msg

    return render(request, "reviews.html", context)

def search_suggest(request):
    q = request.GET.get("q", "")
    books = Book.objects.filter(book_title__icontains=q).values_list("book_title", flat=True)[:5]
    return JsonResponse(list(books), safe=False)

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        # Save in database
        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message,
            date=timezone.now().date()
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "contact.html")

@login_required
def payment(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        payment = Payment.objects.create(
            user=request.user,
            name=request.user.username,
            payment_method=request.POST.get("payment_method"),
            card_num=request.POST.get("card_num") or None,
            upi_id=request.POST.get("upi_id") or None,
            address=request.POST.get("address"),
            contact=request.POST.get("contact"),
        )
        OrderedBook.objects.create(payment=payment, book=book)

        # reduce quantity
        book.quantity -= 1
        if book.quantity <= 0:
            book.quantity = 0
            book.out_of_stock_time = timezone.now()
            book.is_sold = True
        book.save()

        return redirect("success", payment_id=payment.id)

    return render(request, "payment.html", {"book": book})

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from .models import Payment, OrderedBook
from decimal import Decimal
from django.shortcuts import get_object_or_404

@login_required
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    ordered_books_qs = OrderedBook.objects.select_related("book").filter(payment=payment)

    ordered_books = []
    for item in ordered_books_qs:
        price_per_book = item.book.price * Decimal("1.3")
        total_for_item = price_per_book * item.quantity
        ordered_books.append({
            "title": item.book.book_title,
            "author": item.book.author,
            "quantity": item.quantity,
            "price_per_book": price_per_book,
            "total_for_item": total_for_item,
            "photo_url": request.build_absolute_uri(item.book.book_photo.url) if item.book.book_photo else None
        })

    books_total = sum(b['total_for_item'] for b in ordered_books)
    delivery_charges = payment.delivery_charges or Decimal("0")
    platform_fees = payment.platform_fees or Decimal("0")
    grand_total = books_total + delivery_charges + platform_fees

    context = {
        "payment": payment,
        "ordered_books": ordered_books,
        "books_total": books_total,
        "delivery_charges": delivery_charges,
        "platform_fees": platform_fees,
        "grand_total": grand_total,
    }

    html = render_to_string("receipt.html", context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{payment.id}.pdf'

    pisa_status = pisa.CreatePDF(src=html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response


def checkout_success(request):
    return render(request, "checkout_success.html")
