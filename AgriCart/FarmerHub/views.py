from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import razorpay
client = razorpay.Client(auth=("rzp_test_fCVgGqgcfDm0Lh", "oRfjzp64mC7AOuS2XRL5VeaT"))
from django.views.decorators.csrf import csrf_exempt #
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

# Create your views here.

#home page
def index(request):
    products = Product_details.objects.filter(status='Approved').order_by('-id')

    seller_obj = None
    notifications = []

    # ✅ FIX STARTS HERE
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

        seller_obj = Seller_register.objects.filter(user=request.user).first()

        if seller_obj:
            products = Product_details.objects.filter(
                seller=seller_obj,
                status='Approved'
            ).order_by('-id')

            notifications = Notifications.objects.filter(
                seller=seller_obj
            ).order_by('-created_at')
    else:
        wishlist_ids = []
    # ✅ FIX ENDS HERE

    best_sellers = (
        Booking.objects
        .values('product_id')
        .annotate(total_orders=Sum('quantity'))
        .order_by('-total_orders')[:8]
    )

    best_seller_ids = [item['product_id'] for item in best_sellers]

    top_featured_ids = list(
        Product_details.objects.filter(is_top_featured=True)
        .values_list('id', flat=True)
    )

    blogs = Blog.objects.all().order_by('-created_at')

    if request.user.is_authenticated:
        personal = Personal.objects.filter(email=request.user.email).first()

        if personal:
            seller = Seller_register.objects.filter(personal=personal).first()

            if seller:
                blogs = Blog.objects.filter(seller=seller).order_by('-created_at')

    return render(request, 'index.html', {
        'products': products,
        'best_seller_ids': best_seller_ids,
        'top_featured_ids': top_featured_ids,
        'blogs': blogs,
        'notifications': notifications,
        'wishlist_ids': wishlist_ids
    })

#help page
def help_page(request):
    return render(request, 'help.html')

#shop page
from django.db.models import Sum

def shop(request):
    wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    sort = request.GET.get('sort')
    category = request.GET.get('category')

    products = Product_details.objects.filter(status='Approved')

    # ✅ CATEGORY FILTER
    if category:
        products = products.filter(category_id=category)

    # ✅ SORTING
    if sort == 'low':
        products = products.order_by('price')

    elif sort == 'high':
        products = products.order_by('-price')

    elif sort == 'featured':
        products = products.filter(is_top_featured=True)

    elif sort == 'best':
        products = products.annotate(
            total_sold=Sum('booking__quantity')   # ✅ FIXED
        ).order_by('-total_sold')

    categories = Catagories.objects.all()

    return render(request, 'shop.html', {
        'products': products,
        'categories': categories,
        'wishlist_ids': wishlist_ids
    })

#login page
def log_in(request):
    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if CargoTeam.objects.filter(user=user).exists():
                login(request, user)
                return redirect('cargo_dashboard')
            if Seller_register.objects.filter(user=user).exists():
                status = Seller_register.objects.get(user=user).status
                if status == "Approved":
                    login(request, user)  
                    messages.success(request, "Welcome Seller")
                    return redirect('index')
                else:
                    messages.info(request, 'Wait for admin approval')
                    return redirect('log_in')
            login(request, user)
            messages.success(request, 'Welcome')
            return redirect('index')

        else:
            messages.info(request, "Invalid username or password!")
            return redirect('log_in')
    else:
      return render(request, 'log_in.html')

#logout  
def log_out(request):
    logout(request)
    return redirect('log_in')

#buyer register
def buy_reg(request):
    if request.method=='POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        address=request.POST.get('address')
        password=request.POST.get('password')
        re_password=request.POST.get('confirm_password')
        if User.objects.filter(username=email).exists():
            messages.warning(request,"this user is already exists!")
            return redirect('log_in')
        if password != re_password:
            messages.warning(request,"Password does not match")
            return redirect('log_in')
        user=User.objects.create_user(username=email,first_name=name,email=email,password=password)
        user.save()
        buy=Register.objects.create(user=user,name=name,email=email,phone=phone,address=address,password=password)
        buy.save()
        messages.success(request,"user created successfully")
        return redirect('log_in')
    return render(request,'buy_reg.html')

#seller register
def sell_reg(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        password = request.POST.get('password')
        re_password = request.POST.get('confirm_password')
        image = request.FILES.get('image')

        if User.objects.filter(username=email).exists():
            messages.warning(request, "User already exists!")
            return redirect('sell_reg')

        if password != re_password:
            messages.warning(request, "Passwords do not match!")
            return redirect('sell_reg')

        user = User.objects.create_user(
            username=email,
            first_name=name,
            email=email,
            password=password
        )

        Seller_register.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            address=address,
            password=password,
            image=image
        )

        messages.success(request, "Seller registered successfully!")
        return redirect('log_in')

    return render(request, 'sell_reg.html')

#add product
def add_product(request):
    cate = Catagories.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        image = request.FILES.get('image')

        if not category_id:
            messages.error(request, "Please select a category")
            return redirect('add_product')

        category_obj = Catagories.objects.get(id=category_id)

        Product_details.objects.create(
            seller=Seller_register.objects.get(user=request.user),
            product_name=name,
            product_description=description,
            category=category_obj,
            price=price,
            quantity=quantity,
            image=image
        )

        messages.info(request, "Added successfully..")
        return redirect('gallery') 
    return render(request,'add_product.html',{'key': cate})

#gallery page   
def gallery(request):
    cate = Catagories.objects.all()
    wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    seller_obj = Seller_register.objects.filter(user=request.user).first()

    if seller_obj:
        pro = Product_details.objects.filter(
            seller=seller_obj,
            status='Approved'
        ).order_by('-id')
    else:
        pro = Product_details.objects.filter(
            status='Approved'
        ).order_by('-id')

    return render(request, 'sell_pdt_view.html', {
        'key': cate,
        'key2': pro,
        'wishlist_ids': wishlist_ids
    })
    
#edit product
def edit(request,id):
    cate = Catagories.objects.all()
    sell=Product_details.objects.get(id=id)
    if request.method=="POST":
        sell.name = request.POST.get('name')
        sell.description = request.POST.get('description')
        sell.category_id = request.POST.get('category')
        sell.price = request.POST.get('price')
        sell.quantity = request.POST.get('quantity')
        if request.FILES.get('image'):
            sell.image=request.FILES.get('image')
        sell.save()
        return redirect('gallery')
    return render(request,'update.html',{'edit':sell,'key':cate})

#delete product
def delete(request,id):
    sell=Product_details.objects.get(id=id)
    sell.delete()
    return redirect('gallery')

#about us page
def about(request):
    avg_rating = SiteRating.objects.aggregate(Avg('rating'))
    return render(request,'about.html',{'avg_rating': avg_rating})

#contact us page
def contact_us(request):
    avg_rating = SiteRating.objects.aggregate(Avg('rating'))
    return render(request,'contact-us.html',{'avg_rating': avg_rating})

#checkout page
def checkout(request):
    if request.user.is_authenticated:
        buyer = Register.objects.get(user=request.user)
        cart = Cart.objects.filter(buyer=buyer)
        check = Cart.objects.filter(buyer=buyer)

        total_price = sum(i.total_amount for i in check)
        generic_offer = total_price * 0.01

        if not Booking.objects.filter(buyer=buyer).exists():
            off = 'offer'
            first_order_discount = total_price * 0.20
        else:
            off = None
            first_order_discount = 0

        offer_price = generic_offer + first_order_discount
        tax = total_price * 0.005
        grand_total = total_price - (offer_price + tax)

        if request.method == "POST":
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            address = request.POST.get('address')
            country = request.POST.get('country')
            state = request.POST.get('state')
            pin = request.POST.get('pin')

            # Save personal orders
            for i in check:
                Personal.objects.create(
                    buyer=buyer,
                    seller=i.seller,
                    product=i.product,
                    quantity=i.quantity,
                    firstname=fname,
                    lastname=lname,
                    email=email,
                    address=address,
                    country=country,
                    state=state,
                    pin=pin,
                    amount=i.total_amount
                )

            # Razorpay order data
            DATA = {
                "amount": int(grand_total * 100),  # in paise
                "currency": "INR",
                "receipt": f"receipt_{request.user.id}",
                "payment_capture": 1
            }

            razorpay_order = client.order.create(DATA)
            order_id = razorpay_order['id']

            return JsonResponse({
                'order_id': order_id,
                'status': 'order created',
                'price': grand_total
            })

        return render(request, 'checkout.html', {
            'check': check,
            'total_price': total_price,
            'off': off,
            'offer_price': offer_price,
            'cart': cart,
            'tax': tax,
            'grand_total': grand_total,
            'generic_offer': generic_offer
        })

#my account page
@login_required
def my_account(request):

    user = request.user

    # Try to get buyer profile
    buyer = Register.objects.filter(email=user.email).first()

    # Try to get seller profile
    seller = Seller_register.objects.filter(email=user.email).first()

    # Orders (only for buyers)
    orders = Booking.objects.filter(buyer__email=user.email).order_by('-id')

    context = {
        'user': user,
        'buyer': buyer,
        'seller': seller,
        'orders': orders
    }

    return render(request, 'my-account.html', context)

#product view page
def view_pdt(request, id):
    wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    if not request.user.is_authenticated:
        return redirect('log_in')

    product = Product_details.objects.get(id=id)
    reviews = Review.objects.filter(product=product)
    pro = Product_details.objects.filter(status='Approved', quantity__gte=0)
    seller = Seller_register.objects.filter(user=request.user).exists()
    


    products= Product_details.objects.filter(status='Approved').order_by('-id')


    seller_obj = Seller_register.objects.filter(user=request.user).first()

    if seller_obj:
        products = Product_details.objects.filter(
            seller=seller_obj,
            status='Approved'
        ).order_by('-id')
    else:
        products = Product_details.objects.filter(
            status='Approved'
        ).order_by('-id')


    if request.method == "POST":
        buyer = Register.objects.get(email=request.user.email)
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        existing = Review.objects.filter(product=product, buyer=buyer).first()
        if existing:
            messages.warning(request, "You already reviewed this product")
        else:
            Review.objects.create(
                product=product,
                buyer=buyer,
                comment=comment,
                rating=rating
            )

            messages.success(request, "Review added successfully")
            return redirect('view_pdt', id=id)
    
    
    return render (request, 'view_pdt.html', {
        'product': product,
        'key2': pro,
        'seller': seller,  
        'reviews': reviews,
        'products': products,
        'wishlist_ids': wishlist_ids
    })

#cart view page
def cart_view(request):
    cart = Cart.objects.filter(buyer=Register.objects.get(user=request.user))
    buyer = Register.objects.get(user=request.user)
    check = Cart.objects.filter(buyer=buyer)
    total_price = sum(i.total_amount for i in check)
    offer_price =(total_price * 1 / 100)
    tax =(total_price * 0.5 / 100)
    grand_total =(total_price - (offer_price + tax))
    return render(request, 'cart.html', {'cart': cart,'check': check,'total_price': total_price,'offer_price':offer_price,'tax':tax,'grand_total':grand_total})

#wishlist page

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product_details, id=product_id)

    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    # TOGGLE WISHLIST (ADD / REMOVE)
    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        Wishlist.objects.create(user=request.user, product=product)

    return redirect(request.META.get('HTTP_REFERER', 'home'))

#view wishlist page
@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'items': items})

#remove product from wishlist
@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    return redirect('wishlist_view')

#add to cart
def add_to_cart(request, id):
    if not request.user.is_authenticated:
        return redirect('log_in')

    buyer = Register.objects.get(user=request.user)
    product = get_object_or_404(Product_details, id=id)

    quantity = int(request.POST.get('quantity', 1))

    # ✅ Check stock
    if product.quantity == 0:
        messages.error(request, "Out of stock!")
        return redirect(request.META.get('HTTP_REFERER'))

    if quantity > product.quantity:
        messages.warning(request, f"Only {product.quantity} available")
        return redirect(request.META.get('HTTP_REFERER'))

    # ✅ Check if already exists in cart
    cart_item = Cart.objects.filter(buyer=buyer, product=product).first()

    if cart_item:
        new_qty = cart_item.quantity + quantity

        if new_qty > product.quantity:
            messages.warning(request, f"Only {product.quantity} available")
            return redirect(request.META.get('HTTP_REFERER'))

        cart_item.quantity = new_qty
        messages.info(request, "Product already in cart. Quantity updated!")
    else:
        cart_item = Cart.objects.create(
            buyer=buyer,
            product=product,
            seller=product.seller,
            quantity=quantity,
            total_amount=quantity * product.price
        )
        messages.success(request, "Added to cart successfully ")

    # ✅ Update total
    cart_item.total_amount = cart_item.quantity * product.price
    cart_item.save()

    # ✅ Reduce stock
    product.quantity -= quantity
    product.save()

    # ✅ REMOVE FROM WISHLIST (IMPORTANT)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    if wishlist_item:
        wishlist_item.delete()
        messages.info(request, "Removed from wishlist")

    return redirect('cart_view')

#delete from cart
def dele(request, id):
    cart_item = Cart.objects.get(id=id)
    product = cart_item.product

    # ✅ RESTORE STOCK
    product.quantity += cart_item.quantity
    product.save()

    cart_item.delete()

    messages.success(request, "Removed from cart")
    return redirect('cart_view')

#update cart
def update_cart(request):
    if request.method == "POST":
        buyer = Register.objects.get(user=request.user)
        cart_items = Cart.objects.filter(buyer=buyer)

        for item in cart_items:
            new_qty = request.POST.get(f'quantity_{item.id}')

            if new_qty:
                new_qty = int(new_qty)
                product = item.product

                old_qty = item.quantity
                diff = new_qty - old_qty

                # 🔴 Increasing
                if diff > 0:
                    if diff > product.quantity:
                        messages.error(request, f"Only {product.quantity} available")
                        return redirect('cart_view')

                    product.quantity -= diff

                # 🔴 Decreasing
                elif diff < 0:
                    product.quantity += abs(diff)

                item.quantity = new_qty
                item.total_amount = new_qty * product.price
                item.save()

                product.save()

        return redirect('cart_view')

#payment page   
@csrf_exempt
def payment_success(request,id):
    if request.method=="POST":
        try:
            buyer=Register.objects.get(user=User.objects.get(id=id))
            cart_items=Cart.objects.filter(buyer=buyer)
            for i in cart_items:
                book = Booking.objects.create(
                    buyer=buyer,
                    seller=i.seller,
                    product=i.product,
                    quantity=i.quantity,
                    amount=i.total_amount,
                    status='Paid',
                    delivery_status='Confirmed'
                )

                # ✅ create notification immediately for THIS booking
                Notifications.objects.create(
                    buyer=buyer,
                    seller=i.seller,
                    product=i.product,
                    booking=book,   # ✅ correct mapping
                    quantity=i.quantity,
                    amount=i.total_amount,
                    notification=f"New order for {i.product.product_name}"
                )   
                
            for item in cart_items:
                
                item.product.save()
            try:
                html_message = f"""
                <html>
                  <head>
                    <style>
                      body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        color: #333;
                        padding: 20px;
                      }}
                      .container {{
                        width: 80%;
                        margin: auto;
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                      }}
                      h2 {{
                        color: #4CAF50;
                      }}
                      table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                      }}
                      th, td {{
                        padding: 12px;
                        border: 1px solid #ddd;
                        text-align: left;
                      }}
                      th {{
                        background-color: #f2f2f2;
                      }}
                      .total {{
                        font-size: 1.2em;
                        font-weight: bold;
                        color: #4CAF50;
                      }}
                      .footer {{
                        margin-top: 20px;
                        text-align: center;
                        font-size: 0.9em;
                        color: #999;
                      }}
                    </style>
                  </head>
                  <body>
                    <div class="container">
                      <h2>Farmershub Booking Confirmation</h2>
                      <p>Dear {request.user.first_name} {request.user.last_name},</p>
                      <p>Thank you for your order! Your booking has been successfully processed. Below are the details of your booking:</p>

                      <h3>Booking Details</h3>
                      <table>
                        <tr><th>Buyer Name</th><td>{buyer.name}</td></tr>
                        <tr><th>Email</th><td>{buyer.email}</td></tr>
                      </table>

                      <h3>Ordered Products</h3>
                      <table>
                        <tr><th>Product Name</th><th>Quantity</th><th>Total Amount</th></tr>
                        {''.join([f'<tr><td>{item.product.product_name}</td><td>{item.quantity}</td><td>₹{item.total_amount}</td></tr>' for item in cart_items])}
                      </table>


                      <div class="footer">
                        <p>Thank you for choosing Farmershub. If you have any questions or need assistance, feel free to contact us.</p>
                      </div>
                    </div>
                  </body>
                </html>
                """

                send_mail(
                    subject='Farmerhub Booking Confirmation',
                    message='Thank you for your order.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    html_message=html_message,
                    fail_silently=False
                )

            except Exception as email_error:
                print("Email error:", email_error)
            
            cart_items.delete()  # Empty the cart regardless of email success
            return JsonResponse({'status': 'success'})

        except Exception as main_error:
            print("Main error:", main_error)
            return JsonResponse({'status': 'error', 'message': str(main_error)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}) 

#my account
def account(request):
    if Register.objects.filter(user=request.user).exists():
        buyer=Register.objects.get(user=request.user)
        bookings=Booking.objects.filter(buyer=buyer)
        roll='buyer'
    elif Seller_register.objects.filter(user=request.user).exists():
        seller=Seller_register.objects.get(user=request.user)
        bookings=Booking.objects.filter(seller=seller)
        roll='seller'
    return render(request, 'my-account.html',{'roll':roll, 'bookings':bookings})

#tracking order
@login_required
def track_order(request):
    orders = Booking.objects.filter(
        buyer__email=request.user.email   # adjust if needed
    ).order_by('-id')

    return render(request, 'tracking.html', {'orders': orders})

#track delivery
@login_required
def track_delivery(request, id):
    book = Booking.objects.filter(
        id=id,
        buyer__email=request.user.email
    ).first()

    return render(request, 'track_delivery.html', {'book': book})

#add blog
@login_required
def add_blog(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        try:
            seller_obj = Seller_register.objects.get(user=request.user)

            Blog.objects.create(
                seller=seller_obj,
                title=title,
                content=content,
                image=image
            )

            print("Blog created successfully")

        except Exception as e:
            print("ERROR:", e)
            return redirect('index')

        return redirect('view_blogs')

    return render(request, 'add_blog.html')

#view blog
def view_blogs(request):

    blogs = Blog.objects.all().order_by('-created_at')

    if request.user.is_authenticated:

        personal = Personal.objects.filter(email=request.user.email).first()

        if personal:
            seller = Seller_register.objects.filter(personal=personal).first()

            if seller:
                blogs = Blog.objects.filter(seller=seller).order_by('-created_at')

    return render(request, 'blogs.html', {'blogs': blogs})

#view blog detail
@login_required
def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)

    if request.method == 'POST':
        # COMMENT
        if 'comment_submit' in request.POST:
            text = request.POST.get('comment')
            if text:
                Comment.objects.create(
                    blog=blog,
                    user=request.user,
                    text=text
                )

        # LIKE
        if 'like_submit' in request.POST:
            if request.user in blog.likes.all():
                blog.likes.remove(request.user)
            else:
                blog.likes.add(request.user)

        return redirect('blog_detail', id=id)

    return render(request, 'blog_detail.html', {'blog': blog})

#share blog
@login_required
def share_blog(request, id):
    blog = get_object_or_404(Blog, id=id)
    blog.shares += 1
    blog.save()
    return redirect('blog_detail', id=id)

#delete blog
@login_required
def delete_blog(request, id):
    blog = get_object_or_404(Blog, id=id)

    # ✅ Allow only owner (seller) to delete
    try:
        personal = Personal.objects.filter(email=request.user.email).first()
        seller = Seller_register.objects.filter(personal=personal).first()

        if blog.seller == seller:
            blog.delete()
    except:
        pass

    return redirect('view_blogs')

#order details of seller
from datetime import timedelta

def order_details(request, id):

    if not request.user.is_authenticated:
        return redirect('log_in')

    order_items = Booking.objects.none()

    buyer = Register.objects.filter(user=request.user).first()
    seller = Seller_register.objects.filter(user=request.user).first()

    if buyer:
        order_items = Booking.objects.filter(id=id, buyer=buyer)

    elif seller:
        order_items = Booking.objects.filter(id=id, seller=seller)

    # ✅ CORRECT LOGIC
    for order in order_items:
        notification = Notifications.objects.filter(booking=order).first()

        if notification and notification.created_at:
            order.pickup_time = notification.created_at + timedelta(hours=6)

    return render(request, 'order_details.html', {
        'order_items': order_items
    })

#order history of buyer
def order_history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_register = Register.objects.get(email=request.user.email)

    orders = Booking.objects.filter(buyer=user_register).order_by('-id')

    return render(request, 'order_history.html', {'orders': orders})

#edit my profile
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_email = request.user.email

    buyer = Register.objects.filter(email=user_email).first()
    seller = Seller_register.objects.filter(email=user_email).first()

    if buyer:
        profile = buyer
        user_type = 'buyer'
    elif seller:
        profile = seller
        user_type = 'seller'
    else:
        return redirect('login')

    if request.method == 'POST':
        profile.name = request.POST.get('name')
        profile.phone = request.POST.get('phone')


        profile.save()
        return redirect('my_account')

    return render(request, 'edit_profile.html', {
        'profile': profile,
        'user_type': user_type
    })

#website rating
def add_site_rating(request):

    if request.method == "POST":
        rating = request.POST.get('rating')
        review = request.POST.get('review')

        # CHECK IF USER ALREADY REVIEWED
        existing = SiteRating.objects.filter(user=request.user).first()

        if existing:
            messages.warning(request, "You have already reviewed this site.")
            return redirect(request.META.get('HTTP_REFERER'))

        # SAVE NEW REVIEW
        SiteRating.objects.create(
            user=request.user,
            rating=rating,
            review=review
        )
    
        messages.success(request, "Thank you for your review!")

    return redirect(request.META.get('HTTP_REFERER'))

#seller otifications
@login_required
def open_notification(request, id):
    notification = get_object_or_404(Notifications, id=id)

    notification.markasread = True
    notification.save()

    if notification.booking:
        return redirect('order_details', id=notification.booking.id)

    booking = Booking.objects.filter(
        product=notification.product,
        buyer=notification.buyer,
        seller=notification.seller
    ).order_by('-id').first()

    if booking:
        return redirect('order_details', id=booking.id)

    return redirect('index')

from django.shortcuts import render
from .models import Booking, Seller_register

def seller_order_history(request):
    seller = Seller_register.objects.filter(user=request.user).first()

    orders = Booking.objects.filter(product__seller=seller).order_by('-id')

    search = request.GET.get('search')
    if search:
        orders = orders.filter(product__product_name__icontains=search)

    # attach notification for each booking
    for order in orders:
        order.notification = Notifications.objects.filter(
            booking=order,
            seller=seller
        ).first()

    return render(request, 'seller_order_history.html', {
        'orders': orders
    })

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required




from datetime import timedelta

@login_required
def cargo_dashboard(request):

    if not CargoTeam.objects.filter(user=request.user).exists():
        return redirect('log_in')

    today = timezone.now()
    last_week = today - timedelta(days=7)

    notifications = Notifications.objects.filter(created_at__gte=last_week)

    weekly_orders = (
        notifications
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    bookings = Booking.objects.filter(status='Paid').order_by('-id')

    # ✅ ADD THIS BLOCK (IMPORTANT 🔥🔥🔥)
    for order in bookings:
        notification = Notifications.objects.filter(booking=order).first()

        if notification and notification.created_at:
            order.pickup_time = notification.created_at + timedelta(hours=6)
        else:
            order.pickup_time = None
    # -----------------------------------

    new_orders = bookings.filter(delivery_status='Confirmed').count()
    ongoing_orders = bookings.filter(delivery_status__in=['Shipped', 'Out For Delivery']).count()
    delivered_orders = bookings.filter(delivery_status='Delivered').count()

    total_earnings = bookings.aggregate(total=Sum('amount'))['total'] or 0

    total_customers = Register.objects.count()
    paying_customers = bookings.values('buyer').distinct().count()
    non_paying = total_customers - paying_customers


    return render(request, 'dashboard.html', {
        'bookings': bookings,

        'new_orders': new_orders,
        'ongoing_orders': ongoing_orders,
        'delivered_orders': delivered_orders,

        'weekly_orders': list(weekly_orders),

        'total_earnings': total_earnings,

        'total_customers': total_customers,
        'paying_customers': paying_customers,
        'non_paying': non_paying,
        

    })
from datetime import timedelta

@login_required
def update_delivery_status(request, id):
    booking = get_object_or_404(Booking, id=id)

    if request.method == "POST":
        new_status = request.POST.get('status')

        if booking.delivery_status != new_status:
            booking.delivery_status = new_status
            booking.save()

            # 📧 Email
            send_mail(
                "Delivery Status Updated",
                f"Dear {booking.buyer.user.first_name},\nYour order status is now: {new_status}",
                settings.EMAIL_HOST_USER,
                [booking.buyer.email],
                fail_silently=False
            )

            # 🔔 Notification (FIXED)
            Notifications.objects.create(
                buyer=booking.buyer,
                seller=booking.seller,
                product=booking.product,
                booking=booking,
                quantity=booking.quantity,
                amount=booking.amount,
                notification=f"Order #{booking.id} is now {new_status}"
            )

    return redirect('cargo_dashboard')
