from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {} #we dont want to see anything in the admin
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1]) #this will bring us the cart items
            for cart_item in cart_items: #access cart item quantity
                cart_count += cart_item.quantity #initialize cart_count to zero up
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)