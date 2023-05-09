from django.shortcuts import redirect, render, get_object_or_404
from store.models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from django.http import HttpResponse
from orders.models import OrderProduct
#Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator




def store(request,category_slug=None):

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {'products': paged_products, 'product_count': product_count}
    
    
    return render(request,'store/store.html', context=context)

def product_detail(request, category_slug, product_slug):
    
    single_product = Product.objects.get(category__slug=category_slug, slug=product_slug )
    
    if request.user.is_authenticated is not True:
        order_product = None
    else:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id = single_product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
            
    reviews = ReviewRating.objects.filter(product=single_product, status=True)
    
    #Get product Gallery
    product_gallery = ProductGallery.objects.filter(product=single_product)
    
    context = {
        'single_product':single_product,
        'order_product': order_product,
        'reviews':reviews,
        'product_gallery':product_gallery,
        }
    return render(request,'store/product_detail.html', context=context)

def search(request):
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
            'products': products,
            'product_count': product_count,
            'keyword':keyword,
        }
    return render(request,'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    print('url:'+ url)
    ip = request.META.get('REMOTE_ADDR')
    print('dirección ip:' + ip)
    
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request,'Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review_rating = ReviewRating(
                    subject = form.cleaned_data['subject'],
                    rating = form.cleaned_data['rating'],
                    review = form.cleaned_data['review'],
                    ip = request.META.get('REMOTE_ADDR'),
                    product_id = product_id,
                    user_id = request.user.id,
                )
                review_rating.save()
                messages.success(request,'Your review has been submited')
                return redirect(url)
            else:
                return HttpResponse('Mal formulario')