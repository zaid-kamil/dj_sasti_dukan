from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib import messages

def logout_view(request):
    logout(request)
    return redirect('home')

def home_view(request):
    return render(request, 'home.html')

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