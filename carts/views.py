from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product,Variation
from . models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
  
# function to get session id 
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #this will get the product
    # if the user is authenticated
    if current_user.is_authenticated:
        # make a list of objects with variation 
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation) #go and store this product_variation in cartItem model
                except:
                    pass
                
            # add the product to cart 
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()#will return True or False
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user=current_user)
            ex_var_list = []#is the product existing in the database
            id = [] #id of the product
            for item in cart_item:
                existing_variations = item.variations.all()
                ex_var_list.append(list(existing_variations))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                #increase cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                #create new cart item
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0: #check if the project list is empty or not
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            #we create a new cart item
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user    =   current_user,
            )
            if len(product_variation) > 0: #check if the project list is empty or not
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    
    #if the user is not authenticated  
    else:
        # make a list of objects with variation 
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation) #go and store this product_variation in cartItem model
                except:
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using cart id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()
            # add the product to cart 
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()#will return True or False
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            # existing_variations -> database
            # current_variations -> product_variation
            # ite_id -> database
            ex_var_list = []#is the product existing in the database
            id = []
            for item in cart_item:
                existing_variations = item.variations.all()
                ex_var_list.append(list(existing_variations))
                id.append(item.id)
                
            print(ex_var_list)
            
            if product_variation in ex_var_list:
                #increase cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                #create new cart item
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0: #check if the project list is empty or not
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            #we create a new cart item
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0: #check if the project list is empty or not
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('cart')
    
    
def remove_cart(request, product_id, cart_item_id):  
    product = get_object_or_404(Product, id=product_id) # get the product 
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart
            cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id) 
        if cart_item.quantity > 1:
            cart_item.quantity -= 1 # it will decrement the quantity
            cart_item.save()
        else:
            cart_item.delete #to delete the cart item
    except:
        pass
    return redirect('cart')      

def remove_cart_item(request, product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id) # get the product
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart
        cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id) #get the cart item
    cart_item.delete() #when click remove everything, no increment or decrement
    return redirect('cart')
            
def cart(request,total=0, quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:    
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total       += (cart_item.product.price * cart_item.quantity)
            quantity    += cart_item.quantity
             
        tax = (2 * total)/100 # add 2% of total amount
        grand_total = total + tax # calc the grand total 
    except ObjectDoesNotExist:#CartItem.DoesNotExist
        pass #just ignore
    context = {
        'total'         : total,
        'quantity'      : quantity,
        'cart_items'    : cart_items,
        'tax'           : tax,
        'grand_total'   :grand_total,
    }
    return render(request, 'store/cart.html',context)

@login_required(login_url='signin')
def checkout(request,total=0, quantity=0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:    
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total       += (cart_item.product.price * cart_item.quantity)
            quantity    += cart_item.quantity
             
        tax = (2 * total)/100 # add 2% of total amount
        grand_total = total + tax # calc the grand total 
    except ObjectDoesNotExist:#CartItem.DoesNotExist
        pass #just ignore
    context = {
        'total'         : total,
        'quantity'      : quantity,
        'cart_items'    : cart_items,
        'tax'           : tax,
        'grand_total'   :grand_total,
    }
    return render(request,'store/checkout.html',context)
