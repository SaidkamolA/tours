from django.db import models
from avtorizate.models import User

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_num = models.CharField(max_length=16, unique=True)
    mm_yy = models.CharField(max_length=5)
    balance = models.IntegerField(default=10000)

    def __str__(self):
        return self.card_num

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField()
    from_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='outgoing_transactions', null=True)
    to_card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='incoming_transactions', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return f"{self.value} - {self.category.name}"
