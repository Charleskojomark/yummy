# my_app/urls.py
from django.urls import path
from . import views  

app_name = 'reservation'

urlpatterns = [
    path('', views.meal_list, name='meal_list'),
    path('meal/<int:meal_id>/', views.meal_detail, name='meal_detail'),
    path('book/<int:meal_id>/', views.book_meal, name='book_meal'),
    path('orders/', views.orders, name='orders'),
    path('fund/', views.fund_account, name='fund_account'),
    path('paystack-webhook/', views.paystack_webhook, name='paystack_webhook'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('verify-payment/<str:ref>/', views.verify_payment, name='verify_payment'),
    path('initiate-payment/update/', views.paystack_webhook, name='webhook'),
    
]
