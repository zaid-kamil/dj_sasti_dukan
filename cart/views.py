from django.shortcuts import render, redirect
from .models import Order, Cart, CartItem
from product.models import Product

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, 
                                        settings.RAZOR_KEY_SECRET))

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        pid = request.POST.get('product_id')
        product = Product.objects.get(id=pid)
        currency = 'INR'
        amount = int(product.price * 100) # amount in paisa
        # create a razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': currency,
            'payment_capture': '0' # auto capture
        })
        razorpay_order_id = razorpay_order['id']
        callback_url = request.build_absolute_uri('/payment/callback')
        request.session['product_id'] = pid
        ctx = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'currency': currency,
            'callback_url': callback_url,
            'product': product
        }
        return render(request, 'cart/checkout.html', ctx)
    messages.error(request, 'Invalid request')  
    return redirect('home')  

# this function will be called after the payment is done
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        # get the required parameters from post request.
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        print(result)
        if result:
            try:
                product = Product.objects.get(id=request.session['product_id'])
                order = Order(
                    user=request.user,
                    product=product,
                    address='12/123, abc street, xyz city',
                    is_paid = True,
                )
                order.save()
                razorpay_client.payment.capture(payment_id, int(order.product.price*100))
                return render(request, 'cart/success.html')
            except:
                messages.error(request, 'Failed to save order')
                return render(request, 'cart/failure.html')
        else:
            messages.error(request, 'Invalid payment details')
            return render(request, 'cart/failure.html')
    # if this url is accessed directly
    messages.error(request, 'Invalid request')
    return redirect('home')

def success_view(request):
    order = Order.objects.get(id=request.session['payment_info']['ORDERID'])
    return render(request, 'cart/success.html', {'order': order})

def failure_view(request):
    order = Order.objects.get(id=request.session['payment_info']['ORDERID'])
    return render(request, 'cart/failure.html', {'order': order})

@login_required
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        total = 0
        for item in items:
            total += item.product.price * item.quantity
        if request.method == 'POST':
            currency = 'INR'
            razorpay_order = razorpay_client.order.create({
                'amount': int(total * 100),
                'currency': currency,
                'payment_capture': '0'
            })
            razorpay_order_id = razorpay_order['id']
            callback_url = request.build_absolute_uri('/cart/callback')
            ctx = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_merchant_key': settings.RAZOR_KEY_ID,
                'razorpay_amount': int(total * 100),
                'currency': currency,
                'callback_url': callback_url,
                'items': items,
                'total': total,
                'from_cart': True
            }
            return render(request, 'cart/checkout.html', ctx)
        return render(request, 'cart/view.html', {'items': items, 'total': total})
    except:
        return render(request, 'cart/view.html', {'items': []})

@login_required
def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    try:
        cart = Cart.objects.get(user=request.user)
        print("Cart already exists")
    except:
        cart = Cart.objects.create(user=request.user)
        print("New cart created")
    # if product exists in cart increase the quantity
    if CartItem.objects.filter(product=product, cart=cart).first():
        item = CartItem.objects.get(product=product, cart=cart)
        item.quantity += 1
        item.save()
        messages.success(request, 'Product quantity increased')
    else:
        item = CartItem.objects.create(product=product, cart=cart)
        messages.success(request, 'Product added to cart')
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def remove_from_cart(request, id):
    product = Product.objects.get(id=id)
    cart = Cart.objects.get(user=request.user)
    if not cart:
        return redirect('home')
    item = CartItem.objects.filter(product=product, cart=cart).first()
    if item:
        item.delete()
        messages.success(request, 'Product removed from cart')
    return redirect('cart_view')
    

@login_required
@csrf_exempt
def cart_callback(request):
    if request.method == 'POST':
        # get the required parameters from post request.
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        print(result)
        if result:
            # try:
                cart = Cart.objects.get(user=request.user)
                items = CartItem.objects.filter(cart=cart)
                total = 0
                for item in items:
                    total += item.product.price * item.quantity
                    Order.objects.create(
                        user = request.user,
                        product = item.product,
                        quantity = item.quantity,
                        is_paid = True,
                        address = '12/123, abc street, xyz city'
                    )
                razorpay_client.payment.capture(payment_id, int(total*100))
                # destroy the cartitem and cart
                items.delete()
                cart.delete()

                return render(request, 'cart/success.html')
            # except:
            #     messages.error(request, 'Failed to save order')
            #     return render(request, 'cart/failure.html')
        else:
            messages.error(request, 'Invalid payment details')
            return render(request, 'cart/failure.html')
    # if this url is accessed directly
    messages.error(request, 'Invalid request')
    return redirect('home')
