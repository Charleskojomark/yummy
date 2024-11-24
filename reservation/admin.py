from django.contrib import admin

# Register your models here.
from .models import Meal,Transaction,Order

admin.site.register(Meal)
admin.site.register(Transaction)
admin.site.register(Order)