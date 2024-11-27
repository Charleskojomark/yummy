# my_app/urls.py
from django.urls import path
from . import views  

app_name = 'core'


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard') ,   
    path('starter', views.starter, name="starter") , 
]
