from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib import messages
from product.models import Product, Category

def logout_view(request):
    logout(request)
    return redirect('home')

def home_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    ctx = {
        'products': products,
        'categories': categories
    }
    return render(request, 'home.html', ctx)

def category_view(request,name):
    cat = get_object_or_404(Category, slug=name)
    products = get_list_or_404(Product, category=cat)
    return render(
        request, 'category_listing.html',
        context = {
            'products': products, 
            'categories': Category.objects.all(),
            'cat': cat, 
        }
    )

def detail_view(request, id):
    product = Product.objects.get(id=id)
    # get upto 3 similar products
    similar_products = Product.objects.filter(category=product.category).exclude(id=id).order_by('?')[:3] # order by random
    ctx = {
        'product': product,
        'similar_products': similar_products
    }
    return render(request, 'detail.html', ctx)

# seller views
def seller_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        error = False
        if not username :
            messages.error(request, 'Username is required')
            error = True
        if not password:  
            messages.error(request, 'Password is required') 
            error = True
        if not error:
            # check if user exists
            user = authenticate(username=username, password=password)
            if not user:
                messages.error(request, 'Invalid username or password')
            else:
                # check if user is a seller
                if user.groups.filter(name='seller').exists():
                    login(request, user)
                    messages.success(request, 'You are now logged in as Seller')
                    return redirect('home')
                else:
                    messages.error(request, 'You are not registered as a seller')
    return render(request, 'accounts/seller/login.html')

def seller_register_view(request):

    return render(request, 'accounts/seller/register.html')

def seller_forgot_pass_view(request):
    
    return render(request, 'accounts/seller/forgot_password.html')

# customer views
def customer_login_view(request):
    return render(request, 'accounts/customer/login.html')

def customer_register_view(request):
    return render(request, 'accounts/customer/register.html')

def customer_forgot_pass_view(request):
    return render(request, 'accounts/customer/forgot_password.html')