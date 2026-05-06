from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

# Create your models here.

#buyer register
class Register(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=100, null=True, blank=True)
    email=models.EmailField(null=True, blank=True)
    phone=models.BigIntegerField(null=True, blank=True)
    address=models.CharField(max_length=100,null=True, blank=True)
    password=models.CharField(max_length=8, null=True, blank=True)
    def __str__(self):
        return self.name

#seller register
class Seller_register(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    
    name=models.CharField(max_length=100, null=True, blank=True)
    email=models.EmailField(null=True, blank=True)
    phone=models.IntegerField(null=True, blank=True)
    address=models.CharField(max_length=100, null=True, blank=True)
    password=models.CharField(max_length=8, null=True, blank=True)
    image = models.ImageField(upload_to='media', blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved')],
        default='Pending'
    )
    def __str__(self):
        return self.name

#product categories  
class Catagories(models.Model):
    category=models.CharField(max_length=100 , null=True , blank=True)
    def __str__(self):
        return self.category

#product details  
class Product_details(models.Model):
    STATUS_CHOICES=[
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected')
    ]
    seller=models.ForeignKey(Seller_register,on_delete=models.CASCADE)
    product_name=models.CharField(max_length=100 , null=True, blank=True)
    product_description=models.CharField(max_length=2000 , null=True, blank=True)
    category=models.ForeignKey(Catagories, on_delete=models.CASCADE)
    price=models.BigIntegerField(null=True, blank=True)
    quantity=models.IntegerField(null=True, blank=True)
    image=models.ImageField(upload_to='media', null=True, blank=True)
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_top_featured = models.BooleanField(default=False) 
    def __str__(self):
        return self.product_name

# cart  
class Cart(models.Model):
    product = models.ForeignKey(Product_details, on_delete=models.CASCADE, null=True, blank=True)
    buyer=models.ForeignKey(Register,on_delete=models.CASCADE)
    seller=models.ForeignKey(Seller_register,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    total_amount=models.FloatField()
    def __str__(self):
        return self.product.product_name
    class Meta:
        unique_together = ('product', 'buyer')

#review product 
class Review(models.Model):
    product = models.ForeignKey(Product_details, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Register, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

#Personal details
class Personal(models.Model):
    buyer=models.ForeignKey(Register,on_delete=models.CASCADE)
    seller=models.ForeignKey(Seller_register,on_delete=models.CASCADE)
    product=models.ForeignKey(Product_details,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    firstname=models.CharField(max_length=100)
    lastname=models.CharField(max_length=100)
    email=models.EmailField()
    address=models.TextField()
    country=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    pin=models.IntegerField()
    amount=models.FloatField()
    def __str__(self):
        return self.buyer.user.first_name

#booking order 
class Booking(models.Model):
    STATUS_CHOICES=[
        ('Pending','Pending'),
        ('Paid','Paid'),
        ('Cancel','Cancel')
    ] 
    delivery_choices=[
        ('Confirmed','Confirmed'),
        ('Shipped','Shipped'),
        ('Out For Delivery','Out For Delivery'),
        ('Delivered','Delivered')
    ]
    buyer=models.ForeignKey(Register,on_delete=models.CASCADE)
    seller=models.ForeignKey(Seller_register,on_delete=models.CASCADE)
    product=models.ForeignKey(Product_details,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    amount=models.FloatField()
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending') 
    delivery_status = models.CharField(max_length=100,choices=delivery_choices,default='Confirmed')  
    def __str__(self):
        return self.buyer.user.first_name
    

#blogs
class Blog(models.Model):
    seller = models.ForeignKey(Seller_register, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='medias', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Interactive fields
    likes = models.ManyToManyField(User, blank=True, related_name='liked_blogs')
    shares = models.IntegerField(default=0)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

#comments
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.blog.title}"
  
#wishlist
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product_details, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

#website rating
class SiteRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1 to 5
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

#notifications
class Notifications(models.Model):
    buyer = models.ForeignKey(Register, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller_register, on_delete=models.CASCADE)
    product = models.ForeignKey(Product_details, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)  # ✅ ADD THIS
    quantity = models.IntegerField()
    amount = models.FloatField()
    notification = models.CharField(max_length=1000, blank=True, null=True)
    markasread = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)  # ✅ NEW

    def __str__(self):
        return f"{self.seller.user.username}"
    
class CargoTeam(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return self.user.username
