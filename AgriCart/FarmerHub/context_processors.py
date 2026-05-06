from .models import Seller_register,Notifications

#conditions in all page
def user_types(request):
    if request.user.is_authenticated:
        is_seller = Seller_register.objects.filter(user=request.user).exists()
        is_buyer = not is_seller
    else:
        is_seller = False
        is_buyer = False

    return {
        'is_seller': is_seller,
        'is_buyer': is_buyer,
        'is_guest': not request.user.is_authenticated
    }

#seller notification
def notifications(request):
    is_seller = False
    seller = None
    notices_count = 0
    notifications = []

    if request.user.is_authenticated:
        seller = Seller_register.objects.filter(user=request.user).first()

        if seller:
            is_seller = True

            notifications = Notifications.objects.filter(
                seller=seller
            ).order_by('-created_at')

            notices_count = notifications.filter(markasread=False).count()

    return {
        'is_seller': is_seller,
        'seller': seller,
        'noticecount': notices_count,
        'notifications': notifications   # ✅ ADD THIS
    }