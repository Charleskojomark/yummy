# my_app/views.py
from django.shortcuts import render
from reservation.models import Meal,Order, Transaction

def index(request):
    meals = Meal.objects.all()
    context = {
        'meals': meals
    }
    return render(request, 'index.html', context)


def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user= request.user)
    context = {
        'orders': orders,
        'transactions': transactions
    }
    return render(request, 'dashboard.html', context)

