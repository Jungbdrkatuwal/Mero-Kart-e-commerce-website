import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.urls import reverse
import requests


# Create your views here.

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store')







def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        cart_id = request.session.session_key
        if not cart_id:
            cart_id = request.session.create()
        cart_items = CartItem.objects.filter(cart__cart_id=cart_id)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # e.g. 20250818
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()



            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    return redirect('checkout')


def khalti_initiate(request):
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        try:
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
            
            # Amount should be in paisa
            amount_in_paisa = int(order.order_total * 100)
            
            # Use request.build_absolute_uri to construct full URLs
            return_url = request.build_absolute_uri(reverse('khalti_callback'))
            website_url = request.build_absolute_uri('/')
            
            payload = {
                "return_url": return_url,
                "website_url": website_url,
                "amount": amount_in_paisa,
                "purchase_order_id": order.order_number,
                "purchase_order_name": f"Order {order.order_number}",
                "customer_info": {
                    "name": f"{order.first_name} {order.last_name}",
                    "email": order.email,
                    "phone": order.phone
                }
            }
            
            headers = {
                "Authorization": "Key 5e0ca01fb6a54611928bb3f1e3af9857",
                "Content-Type": "application/json"
            }
            
            response = requests.post("https://khalti.com/api/v2/epayment/initiate/", json=payload, headers=headers)
            res_data = response.json()
            
            if response.status_code == 200:
                payment_url = res_data.get('payment_url')
                return redirect(payment_url)
            else:
                return render(request, 'orders/payments.html', {'order': order, 'error': f"Khalti initiation failed: {res_data}"})
                
        except Order.DoesNotExist:
            return redirect('store')
            
    return redirect('checkout')

def khalti_callback(request):
    pidx = request.GET.get('pidx')
    status = request.GET.get('status')
    transaction_id = request.GET.get('transaction_id')
    amount = request.GET.get('amount')
    purchase_order_id = request.GET.get('purchase_order_id')
    
    if status == 'Completed':
        # Perform lookup
        payload = {"pidx": pidx}
        headers = {
            "Authorization": "Key 5e0ca01fb6a54611928bb3f1e3af9857",
            "Content-Type": "application/json"
        }
        response = requests.post("https://khalti.com/api/v2/epayment/lookup/", json=payload, headers=headers)
        res_data = response.json()
        
        if res_data.get('status') == 'Completed':
            try:
                order = Order.objects.get(order_number=purchase_order_id, is_ordered=False)
                
                # Save Payment info
                payment = Payment(
                    user=order.user,
                    payment_id=transaction_id,
                    payment_method='Khalti',
                    amount_paid=str(res_data.get('total_amount', 0) / 100),
                    status=res_data.get('status')
                )
                payment.save()
                
                order.payment = payment
                order.is_ordered = True
                order.save()
                
                # Move cart items to OrderProduct table
                cart_items = CartItem.objects.filter(user=order.user)
                if cart_items.count() <= 0:
                    cart_id = request.session.session_key
                    if cart_id:
                        cart_items = CartItem.objects.filter(cart__cart_id=cart_id)
                        
                for item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id
                    orderproduct.payment = payment
                    orderproduct.user_id = order.user.id
                    orderproduct.product_id = item.product_id
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.product.price
                    orderproduct.ordered = True
                    orderproduct.save()
                    
                    # Reduce product quantity
                    product = Product.objects.get(id=item.product_id)
                    product.stock -= item.quantity
                    product.save()
                    
                # Clear cart
                cart_items.delete()
                
                # Redirect to order complete
                redirect_url = reverse('order_complete') + f"?order_number={order.order_number}&payment_id={payment.payment_id}"
                return redirect(redirect_url)
                
            except Order.DoesNotExist:
                return redirect('store')
        else:
            # Payment lookup failed or status not completed
            return redirect('store')
    else:
        # Status from callback is not 'Completed'
        return redirect('checkout')