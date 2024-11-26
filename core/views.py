# my_app/views.py
from django.shortcuts import render
from reservation.models import Meal,Order, Transaction
from django.contrib.auth.decorators import login_required

def index(request):
    meals = Meal.objects.all()
    context = {
        'meals': meals
    }
    return render(request, 'index.html', context)

@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user= request.user)
    context = {
        'orders': orders,
        'transactions': transactions
    }
    return render(request, 'dashboard.html', context)

