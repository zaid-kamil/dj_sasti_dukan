from django.shortcuts import render, redirect
from product.models import Product
from .models import Order, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages

@login_required
def initiate_payment(request):
    if request.method == 'POST':
        pid = request.POST.get('product_id')
        product = Product.objects.get(id=pid)
        user = request.user
        # create a new order
        order = Order(
            user=user,
            product=product,
            address='12/123, abc street, xyz city'
        )
        order.save()
        # paytm data for payment
        data_dict = {
            'MID': settings.PAYTM_MID,
            'ORDER_ID': str(order.id),
            'TXN_AMOUNT': str(product.price),
            'CUST_ID': user.email,  
            'INDUSTRY_TYPE_ID': "retail",
            'WEBSITE': "WEBSTAGING",
            'CHANNEL_ID': "WEB",
            'CALLBACK_URL': "http://127.0.0.1:8000/payment/callback",
        }
        # encrypt the data
        checksum = generate_checksum(data_dict, settings.PAYTM_MK)
        data_dict['CHECKSUMHASH'] = checksum
        return render(
            request,
            'cart/redirect.html',
            {
                'data_dict': data_dict,
                'paytm_url': settings.PAYTM_URL
            }
        )
    # if this url is accessed directly
    messages.error(request, 'Invalid request')  
    return redirect('home')  

# this function will be called after the payment is done
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                continue
            paytm_params[key] = str(value[0])
        
        # verify the checksum
        is_valid_checksum = verify_checksum(paytm_params, 
                                            settings.PAYTM_MK, 
                                            paytm_checksum)
        if is_valid_checksum:
            messages.success(request, 'Payment successful')
            return redirect('success')
        else:
            messages.error(request, 'Payment failed')
            return redirect('failed')
    
    # if this url is accessed directly
    messages.error(request, 'Invalid request')
    return redirect('home')


