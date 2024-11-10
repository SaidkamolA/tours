from django.contrib import admin
from .models import User, Card, Category, Transaction


admin.site.register(Card)
admin.site.register(Category)
admin.site.register(Transaction)
