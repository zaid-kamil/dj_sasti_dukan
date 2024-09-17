from django.shortcuts import render, redirect
from product.models import Product
from .models import Order, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
import requests
import json
from . import PaytmChecksum
import datetime

def debugDict(d):
    print('_ _ _ '*10)
    for key, value in d.items():
        print(f'{key} -> {value}')
    print('_ _ _ '*10)

def getTransactionToken(order:Order):
    paytmParams = dict()
    paytmParams["body"] = {
        "requestType"   : "Payment",
        "mid"           : settings.PAYTM_MID,
        "websiteName"   : settings.PAYTM_WEBSITE,
        "orderId"       : str(order.id),
        "callbackUrl"   : settings.PAYTM_CALLBACK_URL,
        "txnAmount"     : {
            "value"     : str(order.product.price),
            "currency"  : "INR",
            },
        "userInfo"  : {
            "custId"  : str(order.user.id),
        },
    }
    checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), settings.PAYTM_MK)
    paytmParams["head"] = {
        "signature"    : checksum
    }
    debugDict(paytmParams)
    post_data = json.dumps(paytmParams)
    
    url = settings.PAYTM_ENVIRONMENT+"/theia/api/v1/initiateTransaction?mid="+settings.PAYTM_MID+"&orderId="+str(order.id)
    print(url)
    
    response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
    debugDict(response)
    
    response_str = json.dumps(response)
    res = json.loads(response_str)
    if res["body"]["resultInfo"]["resultStatus"]=='S':
        token=res["body"]["txnToken"]
    else:
        token=""
    print(f'Transaction Token: {token}')
    return token
def transactionStatus():
    paytmParams = dict()
    paytmParams["body"] = {
        "mid" : settings.PAYTM_MID,
        # Enter your order id which needs to be check status for
        "orderId" : "order_1647237662.654877",
    }
    checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), settings.PAYTM_MK)

    # head parameters
    paytmParams["head"] = {
    "signature" : checksum
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    url = settings.PAYTM_ENVIRONMENT+"/v3/order/status"

    response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
    response_str = json.dumps(response)
    res = json.loads(response_str)
    msg="Transaction Status Response"
    return res['body']

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
        generated_token = getTransactionToken(order)
        if generated_token:
            return render(request, 'cart/redirect.html', {
                'order': order, 
                'token': generated_token,
                'mid': settings.PAYTM_MID,
                'amount': product.price,
                'order_id': order.id,
                'env': settings.PAYTM_ENVIRONMENT,
            })
        else:
            messages.error(request, 'Payment failed')
            return redirect(request.META.get('HTTP_REFERER')) # redirect to the same page
        
    messages.error(request, 'Invalid request')  
    return redirect('home')  

# this function will be called after the payment is done
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        print('_ _ _ '*10)
        print('Received data')
        for key, value in received_data.items():
            print(f'{key} -> {value[0]}')
        print('_ _ _ '*10)
        paytm_checksum = received_data['checksumhash'][0]
        for key, value in received_data.items():
            if key == 'checksumhash':
                continue
            paytm_params[key] = str(value[0])
        
        # verify the checksum
        is_valid_checksum = PaytmChecksum.verify_checksum(paytm_params, 
                                            settings.PAYTM_MK, 
                                            paytm_checksum)
        if is_valid_checksum:
            if paytm_params['RESPCODE'] == '01':
                messages.success(request, 'Payment successful')
                request.session['payment_info'] = paytm_params
                # update the order
                order_id = paytm_params['ORDERID']
                order = Order.objects.get(id=order_id)
                order.is_paid = True
                order.save()
                return redirect('success')
            else:
                messages.error(request, f'Payment failed due to {paytm_params["RESPMSG"]}')
                return redirect('failed')
        else:
            messages.error(request, f'Invalid checksum')
            return redirect('home')
    
    # if this url is accessed directly
    messages.error(request, 'Invalid request')
    return redirect('home')

def success_view(request):
    order = Order.objects.get(id=request.session['payment_info']['ORDERID'])
    return render(request, 'cart/success.html', {'order': order})

def failure_view(request):
    order = Order.objects.get(id=request.session['payment_info']['ORDERID'])
    return render(request, 'cart/failure.html', {'order': order})