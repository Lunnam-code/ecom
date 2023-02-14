from django.shortcuts import render, get_object_or_404
from store.models import Product 
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q


def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        # do the query 
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        #product count
        product_count = products.count()
     
    context = {
        'products': paged_products,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)

def product_detail(request, category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug) #get single product info
        # if the product exists it is going to return true, meaning that it will going to show add to cart button
        # if false that means that product is not in the cart 
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        # return HttpResponse(in_cart) #check if it returns true
        # exit()
        variations = single_product.variation_set.all()
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'variations'    :variations
    }
    return render(request,'store/product_detail.html',context)

def search(request):
    if 'keyword' in request.GET: # reciever what is coming from the url
        keyword = request.GET['keyword']
        if keyword: #to check if keyword is blank or not
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    # pass the product into the context 
    context = {
        'products'      : products,
        'product_count' : product_count,
    }
    return render(request,'store/store.html', context)