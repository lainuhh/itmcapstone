from django.contrib import admin

# Register your models here.

from .models import Event, Expense, ExpensePayment, Membership

admin.site.register(Event)
admin.site.register(Expense)
admin.site.register(ExpensePayment)
admin.site.register(Membership)
