from django.db import models

# Create your models here.

class NewUser(models.Model):
    username=models.CharField(max_length=126,null=True,blank=True)
    email=models.EmailField(unique=True)
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



    



    

    







