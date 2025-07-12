from django.db import models

# Create your models here.

class Nuser(models.Model):
    username=models.CharField(max_length=126)
    email=models.EmailField()
    password=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.username} logged in "
    
class LoginActivity(models.Model):
    username=models.CharField(max_length=126,null=True,blank=True)
    email = models.EmailField(null=True, blank=True)
    login_time = models.DateTimeField()

    def __str__(self):
        return f"{self.username} logged in at {self.login_time}"
    

    
class Contact(models.Model):
    name=models.CharField(max_length=123)
    email=models.CharField(max_length=123)
    phone=models.CharField(max_length=123)
    message=models.TextField()
    date=models.DateField()

    def __str__(self):
        return self.name
    
class Book(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    book_title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    book_photo = models.ImageField(upload_to='book_photos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.book_title

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('credit', 'Credit Card'),
        ('upi', 'UPI'),
        ('cash', 'Cash'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)

    card_num = models.CharField(max_length=16, blank=True, null=True)
    expiry = models.CharField(max_length=5, blank=True, null=True)
    cvv = models.CharField(max_length=3, blank=True, null=True)

    upi_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.name} paid for {self.book.book_title} via {self.payment_method}"



    

    







