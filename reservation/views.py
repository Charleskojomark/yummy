from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Meal, Order, Transaction,Payment 
from userauth.models import UserProfile, User
import requests
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt



@login_required
def meal_list(request):
    meals = Meal.objects.all()
    return render(request, 'meals/meal_list.html', {'meals': meals})

@login_required
def meal_detail(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    return render(request, 'meals/meal_detail.html', {'meal': meal})

@login_required
def book_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    user = request.user
    user_profile = user.userprofile
    
    if user_profile.balance >= meal.price:
        user_profile.balance -= meal.price
        user_profile.save()

        Order.objects.create(user=user, meal=meal)
        messages.error(request, "Booking Successful, Order Created")
        return render(request, 'index.html')
    else:
        messages.error(request, "Insufficient Balance")
        return render(request, 'meals/meal_list.html', {'meals': Meal.objects.all()})

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'meals/orders.html', {'orders': orders})

@login_required
def fund_account(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data = {
            "email": request.user.email,
            "amount": int(float(amount) * 100)  # Convert to kobo
        }
        response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=data)
        response_data = response.json()
        if response_data['status']:
            return redirect(response_data['data']['authorization_url'])
    return render(request, 'meals/fund_account.html')



@login_required
def initiate_payment(request):
    if request.method == "POST":
        amount = request.POST['amount']
        email = request.POST['email']
        payment = Payment.objects.create(amount=amount, email=email, user=request.user)
        

        pk = settings.PAYSTACK_PUBLIC_KEY

        
        user = get_object_or_404(User, email=email)

        context = {
            'field_values': request.POST,
            'payment': payment,
            'paystack_pub_key': pk,
        }
        return render(request, 'meals/make_payment.html', context)

    return render(request, 'meals/fund_account.html')

@login_required
def verify_payment(request, ref):
    payment, created = Payment.objects.get_or_create(ref=ref)
    payment.verified = True
    payment.save()
    messages.success(request, "Successful transaction")
    return redirect('core:index')

@login_required
@csrf_exempt
def paystack_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get('amount')
        user = request.user
        response_data = {}

        wallet = get_object_or_404(UserProfile, user=user)
        wallet.balance += int(amount)
        wallet.save()
        
        response_data = {
            'message': 'Wallet balance updated successfully',
            'new_balance': wallet.balance
        }
            

            
        return JsonResponse(response_data, status=200)
