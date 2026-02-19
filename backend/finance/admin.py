from django.contrib import admin
from .models import Category, Transaction, SavingGoal, SavingContribution, Budget

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(SavingGoal)
admin.site.register(SavingContribution)
admin.site.register(Budget)
