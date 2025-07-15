# from faker import Faker
# import random
# import requests
# from django.core.files.base import ContentFile
# from book_app.models import Book

# fake = Faker()

# def download_image(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         return ContentFile(response.content)
#     return None

# def book_db(n=10):
#     try:
#         for _ in range(n):
#             name = fake.name()
#             email = fake.email()
#             phone = fake.phone_number()
#             book_title = fake.sentence(nb_words=3).strip('.')
#             author = fake.name()
#             condition = random.choice(['New', 'Good', 'Fair', 'Old'])
#             price = random.randint(200, 1500)
#             description = fake.paragraph(nb_sentences=3)

#             # Download image
#             image_url = "https://source.unsplash.com/random/400x400?book"
#             image_file = download_image(image_url)

#             book = Book(
#                 name=name,
#                 email=email,
#                 phone=phone,
#                 book_title=book_title,
#                 author=author,
#                 condition=condition,
#                 price=price,
#                 description=description
#             )

#             # Only save image if download succeeded
#             if image_file:
#                 book.book_photo.save(f"{book_title.replace(' ', '_')}.jpg", image_file, save=True)
#             else:
#                 book.save()
        
#         print(f"{n} fake book entries added successfully.")
#     except Exception as e:
#         print("Error while generating books:", e)
